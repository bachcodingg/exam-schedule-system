"""Command line interface.

    python -m studyplan plan data/exams_lut_2026.json --md plan.md --ics plan.ics
    python -m studyplan guide data/exams_lut_nov_2026.json --out guides
    python -m studyplan docs slides.pdf exam_2025.pdf
    python -m studyplan docs documents/stats2 "documents/calc/*.pdf"
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from . import __version__, estimator, guide, logistics, packs, scheduler, workload
from .documents import DocEstimate, estimate_documents
from .export import to_ics, to_markdown
from .models import CATEGORIES, Exam, InputError, Plan, Profile, load


def expand_documents(base: Path, entries: list[str]) -> list[Path]:
    """Entries are files, folders (every file inside) or glob patterns, relative to `base`.

    Absolute paths and patterns work too.
    """
    paths = []
    for entry in entries:
        path = base / entry
        if path.is_dir():
            paths += sorted(p for p in path.iterdir() if p.is_file())
        elif any(ch in entry for ch in "*?["):
            # glob.glob, unlike Path.glob, also accepts absolute patterns.
            pattern = os.path.join(glob.escape(str(base)), entry)
            paths += sorted(Path(p) for p in glob.glob(pattern) if Path(p).is_file())
        else:
            paths.append(path)
    return list(dict.fromkeys(paths))  # a file matched twice is counted once


@dataclass
class Prepared:
    profile: Profile
    exams: list[Exam]
    estimates: list[estimator.Estimate]
    docs: dict[str, DocEstimate]  # exam name -> its documents, for exams that have some
    plan: Plan
    notes: list[str]
    base: Path  # folder of the input file


def prepare(args: argparse.Namespace) -> Prepared:
    """Load the input, apply --start/--hours, read the documents, estimate and schedule."""
    profile, exams = load(args.input)
    if args.start:
        try:
            profile.start_date = date.fromisoformat(args.start)
        except ValueError:
            raise InputError(f"--start: invalid date {args.start!r}, use YYYY-MM-DD") from None
    if args.hours is not None:
        if not 0 < args.hours <= 24:
            raise InputError(f"--hours must be between 0 and 24, got {args.hours:g}")
        profile.daily_hours = args.hours

    base = Path(args.input).parent
    estimates, doc_notes, all_docs = [], [], {}
    for exam in exams:
        docs = None
        paths = expand_documents(base, exam.documents)
        missing = [p for p in paths if not p.exists()]
        if missing:
            doc_notes.append(f"{exam.name}: documents not found: {', '.join(p.name for p in missing)}")
        found = [p for p in paths if p.exists()]
        if found:
            docs = all_docs[exam.name] = estimate_documents(found, category=exam.category)
            if docs.skipped:
                doc_notes.append(f"{exam.name}: skipped unsupported files: {', '.join(docs.skipped)}")
            if docs.unreadable:
                doc_notes.append(f"{exam.name}: could not read: {', '.join(docs.unreadable)}")
            guessed = max(docs.scores, key=lambda c: docs.scores[c])
            if docs.scores[guessed] and guessed != exam.category:
                doc_notes.append(
                    f"{exam.name}: the documents read like '{guessed}', the input says "
                    f"'{exam.category}'. Check the category."
                )
        estimates.append(estimator.estimate(exam, docs))

    needed = {e.exam: e.hours for e in estimates}
    plan = scheduler.schedule(profile, exams, needed)
    notes = logistics.check(profile, exams) + doc_notes
    return Prepared(profile, exams, estimates, all_docs, plan, notes, base)


def cmd_plan(args: argparse.Namespace) -> int:
    run = prepare(args)
    work = workload.analyse(run.profile, run.exams, run.plan)
    markdown = to_markdown(run.plan, run.exams, run.estimates, run.notes, work)

    if args.md:
        Path(args.md).write_text(markdown, encoding="utf-8")
        print(f"Markdown plan written to {args.md}")
    if args.ics:
        Path(args.ics).write_text(to_ics(run.plan, run.exams, run.profile.timezone), encoding="utf-8", newline="")
        print(f"Calendar written to {args.ics}")
    if not args.md:
        sys.stdout.reconfigure(encoding="utf-8")
        print(markdown)
    return 0


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "exam"


def find_pack(exam: Exam, base: Path) -> packs.Pack | None:
    """The exam's own pack (path relative to the input file), else a matching built-in one."""
    if not exam.pack:
        return packs.find(exam.name)
    path = base / exam.pack
    if not path.exists():
        raise InputError(f"{exam.name}: pack not found: {path}")
    return packs.load(path)


def cmd_guide(args: argparse.Namespace) -> int:
    run = prepare(args)
    work = workload.analyse(run.profile, run.exams, run.plan)
    loads = {load.exam: load for load in work.exams}
    chosen = [e for e in run.exams if not args.exam or e.name.lower() == args.exam.lower()]
    if not chosen:
        names = ", ".join(e.name for e in run.exams)
        raise InputError(f"--exam: no exam named {args.exam!r}, use one of: {names}")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    sys.stdout.reconfigure(encoding="utf-8")
    for exam in chosen:
        pack = find_pack(exam, run.base)
        my_days = {s.day for s in run.plan.sessions if s.exam == exam.name}
        shared = sorted({s.exam for s in run.plan.sessions if s.exam != exam.name and s.day in my_days})
        text = guide.render(
            exam, run.plan, loads[exam.name], run.profile.daily_hours,
            pack=pack, docs=run.docs.get(exam.name), shared_with=shared,
        )
        target = out / f"guide_{slug(exam.name)}.md"
        target.write_text(text, encoding="utf-8")
        content = f"{pack.course} pack" if pack else "no content pack"
        print(f"{exam.name}: {workload.summary(loads[exam.name], run.profile.daily_hours)}. "
              f"Guide ({content}) written to {target}")
    return 0


def cmd_docs(args: argparse.Namespace) -> int:
    paths = expand_documents(Path.cwd(), args.files)
    missing = [p for p in paths if not p.exists()]
    if missing:
        raise InputError(f"not found: {', '.join(str(p) for p in missing)}")
    if not paths:
        raise InputError("no files matched")
    result = estimate_documents(paths, category=args.category)
    print(f"Category: {result.category}  (keyword scores: {result.scores})")
    for d in result.docs:
        print(f"  {Path(d.path).name}: {d.pages} pages, {d.exercises} exercises, "
              f"{d.formula_marks} formula marks ({d.kind})")
    if result.skipped:
        print(f"  skipped (unsupported type): {', '.join(result.skipped)}")
    if result.unreadable:
        print(f"  could not read: {', '.join(result.unreadable)}")
    print(f"Estimated study time from these documents: {result.hours:.1f} h")
    return 0


def _input_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("input")
    parser.add_argument("--start", help="first study day (YYYY-MM-DD), overrides the file")
    parser.add_argument("--hours", type=float, help="study hours per day, overrides the file")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="studyplan", description="Exam-aware study planner")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("plan", help="generate a study plan from an exams JSON file")
    _input_args(p)
    p.add_argument("--md", help="write the plan as Markdown to this file")
    p.add_argument("--ics", help="write the plan as an .ics calendar to this file")
    p.set_defaults(func=cmd_plan)

    g = sub.add_parser("guide", help="write a study guide per exam: workload, method, agendas, content")
    _input_args(g)
    g.add_argument("--out", default="guides", help="folder for the guides (default: guides)")
    g.add_argument("--exam", help="only this exam (its name)")
    g.set_defaults(func=cmd_guide)

    d = sub.add_parser("docs", help="estimate study hours from course documents")
    d.add_argument("files", nargs="+", help="files, folders or glob patterns")
    d.add_argument("--category", choices=CATEGORIES, help="force a category instead of detecting it")
    d.set_defaults(func=cmd_docs)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (InputError, FileNotFoundError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
