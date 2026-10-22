"""Command line interface.

    python -m studyplan plan data/exams_lut_2026.json --md plan.md --ics plan.ics
    python -m studyplan docs slides.pdf exam_2025.pdf
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from . import estimator, logistics, scheduler
from .documents import estimate_documents
from .export import to_ics, to_markdown
from .models import load


def expand_documents(base: Path, entries: list[str]) -> list[Path]:
    """Entries are files, folders (every file inside) or glob patterns, relative to `base`."""
    paths = []
    for entry in entries:
        path = base / entry
        if path.is_dir():
            paths += sorted(p for p in path.iterdir() if p.is_file())
        elif any(ch in entry for ch in "*?["):
            paths += sorted(p for p in base.glob(entry) if p.is_file())
        else:
            paths.append(path)
    return paths


def cmd_plan(args: argparse.Namespace) -> int:
    profile, exams = load(args.input)
    if args.start:
        profile.start_date = date.fromisoformat(args.start)
    if args.hours:
        profile.daily_hours = args.hours

    base = Path(args.input).parent
    estimates, doc_notes = [], []
    for exam in exams:
        docs = None
        paths = expand_documents(base, exam.documents)
        missing = [p for p in paths if not p.exists()]
        if missing:
            doc_notes.append(f"{exam.name}: documents not found: {', '.join(p.name for p in missing)}")
        found = [p for p in paths if p.exists()]
        if found:
            docs = estimate_documents(found, category=exam.category)
            if docs.skipped:
                doc_notes.append(f"{exam.name}: skipped unsupported files: {', '.join(docs.skipped)}")
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
    markdown = to_markdown(plan, exams, estimates, notes)

    if args.md:
        Path(args.md).write_text(markdown, encoding="utf-8")
        print(f"Markdown plan written to {args.md}")
    if args.ics:
        Path(args.ics).write_text(to_ics(plan, exams), encoding="utf-8", newline="")
        print(f"Calendar written to {args.ics}")
    if not args.md:
        sys.stdout.reconfigure(encoding="utf-8")
        print(markdown)
    return 0


def cmd_docs(args: argparse.Namespace) -> int:
    result = estimate_documents(args.files, category=args.category)
    print(f"Category: {result.category}  (keyword scores: {result.scores})")
    for d in result.docs:
        print(f"  {Path(d.path).name}: {d.pages} pages, {d.exercises} exercises, "
              f"{d.formula_marks} formula marks ({d.kind})")
    if result.skipped:
        print(f"  skipped (unsupported type): {', '.join(result.skipped)}")
    print(f"Estimated study time from these documents: {result.hours:.1f} h")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="studyplan", description="Exam-aware study planner")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("plan", help="generate a study plan from an exams JSON file")
    p.add_argument("input")
    p.add_argument("--start", help="first study day (YYYY-MM-DD), overrides the file")
    p.add_argument("--hours", type=float, help="study hours per day, overrides the file")
    p.add_argument("--md", help="write the plan as Markdown to this file")
    p.add_argument("--ics", help="write the plan as an .ics calendar to this file")
    p.set_defaults(func=cmd_plan)

    d = sub.add_parser("docs", help="estimate study hours from course documents")
    d.add_argument("files", nargs="+")
    d.add_argument("--category", help="force a category instead of detecting it")
    d.set_defaults(func=cmd_docs)

    args = parser.parse_args(argv)
    return args.func(args)
