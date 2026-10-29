"""A study guide per exam: workload, method, every session's agenda, and the course content.

The content comes from a pack (studyplan/packs, or the exam's `pack` field). Without one the
guide still has the method and the agendas, plus a template for writing the overviews yourself
and a pointer to the documents to practise from.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from pathlib import Path

from . import method
from .documents import DocEstimate
from .export import topic_hours
from .models import Exam, Plan
from .packs import Pack, PackTopic, demote
from .workload import ExamLoad

TYPE_LABEL = {
    "new": "New topic", "learn": "Learn", "practice": "Practice", "mock": "Mock exam",
    "review": "Review", "review_first": "Review", "review_last": "Review",
}
KIND_HOURS_LABEL = {"learn": "learning", "practice": "spaced practice", "mock": "mock exams", "review": "review"}
OWN_OVERVIEW = [
    "What question does this topic answer? One sentence.",
    "The 3-5 key definitions or formulas, with the conditions they need.",
    "The smallest example you can think of, fully worked.",
    "How do you recognise an exam problem on it, and what is it easily confused with?",
    "The typical trap.",
]


def render(
    exam: Exam,
    plan: Plan,
    load: ExamLoad,
    daily_hours: float,
    pack: Pack | None = None,
    docs: DocEstimate | None = None,
    shared_with: list[str] | None = None,
) -> str:
    agendas = method.plan_agendas(plan, [exam])
    types = method.session_types(plan, [exam])
    mine = sorted(
        (i for i, s in enumerate(plan.sessions) if s.exam == exam.name),
        key=lambda i: (plan.sessions[i].day, plan.sessions[i].start),
    )
    topics = _topics(exam, pack)
    papers = _papers(pack, docs)

    when = f"{exam.exam_date:%a %d.%m.%Y}" + (f" {exam.start:%H:%M}" if exam.start else "")
    if not exam.date_confirmed:
        when += " (date not confirmed)"
    lines = [
        f"# Study guide: {exam.name}",
        "",
        f"**Exam:** {when} · {exam.location} · {exam.duration_h:g} h · target *{exam.target}*  ",
        "**Content:** " + (
            f"{pack.course} pack, {len(pack.topics)} topics" + (" and a practice exam" if pack.exam else "")
            if pack else "no content pack yet (see *Topics* for how to build your own)"
        ),
        "",
        "Work through this guide session by session. Answers are in the appendix so that every "
        "practice problem is a real attempt.",
    ]
    lines += ["", "## 1. Workload", ""] + _workload(load, daily_hours, shared_with or [])
    lines += _weeks(plan, exam, mine)
    lines += ["", "## 2. How to study", ""] + _method(exam.category)
    lines += ["", "## 3. Session by session", ""] + _sessions(plan, exam, mine, types, agendas, papers)
    lines += ["", "## 4. Topics"]
    if not pack:
        lines += [""] + _sources(docs)
    for n, (name, pack_topic) in enumerate(topics, 1):
        lines += [""] + _topic(n, name, pack_topic, plan, exam)
    if pack and pack.exam:
        lines += ["", "## 5. Practice exam", "", demote(pack.exam, 1)]
    lines += _appendix(topics, pack, exam)
    return "\n".join(lines) + "\n"


def _topics(exam: Exam, pack: Pack | None) -> list[tuple[str, PackTopic | None]]:
    """Exam topics with their pack topic; pack topics nobody asked for come last."""
    if not exam.topics:
        return [(t.title, t) for t in pack.topics] if pack else []
    matched = [(t.name, pack.topic_for(t.name) if pack else None) for t in exam.topics]
    used = {id(p) for _, p in matched if p}
    extra = [(f"{t.title} (not in your topic list)", t) for t in (pack.topics if pack else []) if id(t) not in used]
    return matched + extra


def _papers(pack: Pack | None, docs: DocEstimate | None) -> list[str]:
    """Papers for the mock exams: the pack's practice exam first, the real past exams last."""
    papers = ["the practice exam in section 5"] if pack and pack.exam else []
    papers += [Path(d.path).name for d in (docs.docs if docs else []) if d.kind == "past exam"]
    return papers


def _workload(load: ExamLoad, daily_hours: float, shared_with: list[str]) -> list[str]:
    lines = [
        f"- Estimated preparation: **{load.hours:g} h**. At {daily_hours:g} h/day that is "
        f"**{load.pace_days} study days** if this were your only exam.",
        f"- The calendar has **{load.study_days} study days** before the exam"
        + (f", shared with {', '.join(shared_with)}." if shared_with else "."),
    ]
    if load.planned_hours:
        parts = ", ".join(
            f"{load.by_kind[k]:g} h {label}" for k, label in KIND_HOURS_LABEL.items() if load.by_kind.get(k)
        )
        lines.append(
            f"- Planned: **{load.planned_hours:g} h on {load.planned_days} days** "
            f"({load.first:%d.%m}-{load.last:%d.%m}): {parts}."
        )
        extra = load.planned_hours - load.hours
        if extra > 0.5:
            lines.append(
                f"- That is {extra:g} h more than the estimate. The extra time is spaced practice: "
                "use it on your weakest topics."
            )
        elif extra < -0.5:
            lines.append(f"- That is {-extra:g} h short of the estimate: see the warnings in the plan.")
    return lines


def _weeks(plan: Plan, exam: Exam, mine: list[int]) -> list[str]:
    weeks: dict = defaultdict(lambda: [0.0, []])
    for i in mine:
        s = plan.sessions[i]
        week = weeks[s.day - timedelta(days=s.day.weekday())]
        week[0] += s.hours
        for name in (s.topic or "").split(" + ") if s.kind == "learn" else []:
            if name and name not in week[1]:
                week[1].append(name)
    if not weeks:
        return []
    lines = ["", "| Week of | Hours | New material |", "|---|---|---|"]
    for monday, (hours, names) in sorted(weeks.items()):
        lines.append(f"| {monday:%d.%m} | {hours:g} | {'; '.join(n.split(':')[0] for n in names) or '-'} |")
    return lines


def _method(category: str) -> list[str]:
    lines = [
        "The method in one line: **attempt first, learn new topics from worked examples, then "
        "practise retrieval spaced over days and mixed across topics, rehearse the real exam, and "
        "log every mistake until it is fixed.**",
        "",
        "### The five phases",
        "",
        "| Phase | When | What | Why |",
        "|---|---|---|---|",
    ]
    lines += [f"| {p} | {w} | {what} | {why} |" for p, w, what, why in method.PHASES]
    lines += ["", "### The steps of a session", "", "| Step | How |", "|---|---|"]
    lines += [f"| {method.STEP_NAME[k]} | {method.how(k, category)} |" for k in method.STEP_NAME]
    lines += ["", "### Ten rules", ""]
    lines += [f"{n}. {rule}" for n, rule in enumerate(method.RULES, 1)]
    lines += ["", f"**Avoid:** {method.AVOID}", "", "### Why this works", ""]
    lines += [f"- {e}" for e in method.EVIDENCE]
    return lines


def _sessions(plan: Plan, exam: Exam, mine: list[int], types: list[str],
              agendas: list[list[method.Step]], papers: list[str]) -> list[str]:
    lines = []
    mocks = 0
    for i in mine:
        s = plan.sessions[i]
        head = f"**{s.day:%a %d.%m} · {s.start:%H:%M}-{s.end():%H:%M} · {TYPE_LABEL[types[i]]}**"
        if s.topic and s.kind in ("learn", "practice"):
            head += f" · {s.topic}"
        steps = " → ".join(f"{t} {step.name} {step.minutes}′" for t, step in method.timed(s, agendas[i]))
        lines += [f"- {head}  ", f"  {steps}"]
        if s.kind == "mock":
            paper = papers[mocks] if mocks < len(papers) else (
                "a mixed paper: one past-exam problem per topic, weighted by points"
            )
            lines.append(f"  Paper: {paper}.")
            if agendas[i][0].minutes < exam.duration_h * 60:
                lines.append(
                    f"  The block is shorter than the {exam.duration_h:g} h exam: do what fits, choosing "
                    "questions as in the real exam (most points per minute first)."
                )
            mocks += 1
    return lines or ["No sessions planned for this exam."]


def _topic(n: int, name: str, pack_topic: PackTopic | None, plan: Plan, exam: Exam) -> list[str]:
    lines = [f"### Topic {n}: {name}", ""]
    planned = {t.name: (hours, first, last) for t, hours, first, last in topic_hours(plan, exam)}
    if name in planned and planned[name][1]:
        hours, first, last = planned[name]
        lines += [f"*Planned: {hours:.1f} h, {first:%d.%m}-{last:%d.%m}.*", ""]
    if pack_topic:
        for section in ("overview", "worked examples", "common mistakes", "practice"):
            if pack_topic.sections.get(section):
                lines += [f"#### {section.capitalize()}", "", demote(pack_topic.sections[section], 2), ""]
        return lines
    lines += ["#### Write your own beginner overview", "",
              "15 minutes with your notes, then close them and rewrite it from memory:", ""]
    lines += [f"{k}. {q}" for k, q in enumerate(OWN_OVERVIEW, 1)]
    lines += ["", "Then self-explain two solved exercises on this topic and practise on unseen ones, "
              "from easy to exam level."]
    return lines


def _sources(docs: DocEstimate | None) -> list[str]:
    """Where the worked examples and practice come from when there is no pack."""
    files = defaultdict(list)
    for d in docs.docs if docs else []:
        files[d.kind].append(Path(d.path).name)
    lines = ["There is no content pack for this course yet, so the overviews are yours to write "
             "(writing them is itself retrieval practice). Material from your documents:", ""]
    labels = [("solutions", "worked examples to self-explain"), ("material", "lectures and exercises"),
              ("reference", "summaries and formula sheets"), ("past exam", "past exams, kept for the mocks")]
    listed = [f"- {label}: {', '.join(files[kind])}" for kind, label in labels if files.get(kind)]
    lines += listed or ["- none given: add the course files to `documents` in the input file"]
    lines += ["", "To get overviews, worked examples and a practice exam, write a pack in the format "
              "of `studyplan/packs/integral_calculus.md` (or ask Claude to write one from your course "
              "files) and point the exam's `pack` field at it."]
    return lines


def _appendix(topics: list[tuple[str, PackTopic | None]], pack: Pack | None, exam: Exam) -> list[str]:
    lines = []
    answered = [(n, name, t) for n, (name, t) in enumerate(topics, 1) if t and t.sections.get("answers")]
    if answered:
        lines += ["", "## Appendix A: Answers to the practice problems"]
        for n, name, t in answered:
            lines += ["", f"### Topic {n}: {name}", "", demote(t.sections["answers"], 2)]
    if pack and pack.exam_answers:
        lines += ["", "## Appendix B: Practice exam answer key", "", demote(pack.exam_answers, 1)]
    names = [name for name, _ in topics] or [t.name for t in exam.topics] or ["(your topics)"]
    lines += [
        "",
        "## Appendix C: Trackers",
        "",
        "### Mistakes log",
        "",
        "Copy this table to paper or a spreadsheet. Re-solve each entry from a blank page after "
        "1, 3 and 7 days; an entry you get right twice is done.",
        "",
        "| Date | Problem | What went wrong | The fix | Cause | +1 d | +3 d | +7 d |",
        "|---|---|---|---|---|---|---|---|",
        "| | | | | concept / setup / algebra / time | | | |",
        "",
        "### Topic confidence (1 = can't yet, 2 = with help, 3 = alone and on time)",
        "",
        "| Topic | After learning | After practice | After mock 1 | After mock 2 | Review day |",
        "|---|---|---|---|---|---|",
    ]
    lines += [f"| {name.split(':')[0]} | | | | | |" for name in names]
    return lines
