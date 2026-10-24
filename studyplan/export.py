"""Render a plan as Markdown or as an .ics calendar file."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from .estimator import Estimate
from .models import Exam, Plan

KIND_LABEL = {"learn": "Learn", "review": "Review", "mock": "Mock exam", "practice": "Practice"}
DAY_LABEL = {"buffer": "Buffer / rest", "blocked": "Blocked", "exam": "EXAM"}


def to_markdown(plan: Plan, exams: list[Exam], estimates: list[Estimate], notes: list[str]) -> str:
    lines = ["# Study plan", ""]
    lines += ["| Exam | Credits | Date | Place | Estimated h | Planned h |", "|---|---|---|---|---|---|"]
    for exam in sorted(exams, key=lambda e: e.exam_date):
        when = f"{exam.exam_date:%a %d.%m}" + (f" {exam.start:%H:%M}" if exam.start else "")
        if not exam.date_confirmed:
            when += " (assumed)"
        lines.append(
            f"| {exam.name} | {exam.credits:g} | {when} | {exam.location} | "
            f"{plan.needed[exam.name]:.0f} | {plan.scheduled[exam.name]:.0f} |"
        )

    if plan.warnings or notes:
        lines += ["", "## Warnings and logistics", ""]
        lines += [f"- {w}" for w in plan.warnings + notes]

    lines += ["", "## How the estimates were made", ""]
    lines += [f"- **{e.exam}** ({e.source}): {e.detail}" for e in estimates]

    for exam in sorted(exams, key=lambda e: e.exam_date):
        if not exam.topics:
            continue
        lines += ["", f"## Topics: {exam.name}", "", "| Topic | Weight | Planned h | Dates |", "|---|---|---|---|"]
        for topic in exam.topics:
            hits = [s for s in plan.sessions if s.exam == exam.name and s.topic and topic.name in s.topic.split(" + ")]
            when = f"{min(s.day for s in hits):%d.%m}-{max(s.day for s in hits):%d.%m}" if hits else "-"
            hours = sum(s.hours / len(s.topic.split(" + ")) for s in hits)
            lines.append(f"| {topic.name} | {topic.weight:g} | {hours:.1f} | {when} |")

    lines += ["", "## Weekly overview (hours)", ""]
    names = [e.name for e in sorted(exams, key=lambda e: e.exam_date)]
    lines += ["| Week of | " + " | ".join(names) + " |", "|---" * (len(names) + 1) + "|"]
    for monday, hours in sorted(weekly_hours(plan).items()):
        lines.append(f"| {monday:%d.%m} | " + " | ".join(f"{hours.get(n, 0):g}" for n in names) + " |")

    lines += ["", "## Day by day", ""]
    exam_by_day = defaultdict(list)
    for exam in exams:
        exam_by_day[exam.exam_date].append(exam)
    for day, kind in sorted(plan.day_kinds.items()):
        if kind == "exam":
            held = ", ".join(
                f"{e.name}" + (f" {e.start:%H:%M}" if e.start else "") + f" ({e.location.city})"
                for e in exam_by_day[day]
            )
            lines.append(f"- **{day:%a %d.%m} - EXAM: {held}**")
        elif kind in DAY_LABEL:
            lines.append(f"- {day:%a %d.%m} - {DAY_LABEL[kind]}")
        else:
            blocks = "; ".join(
                f"{s.start:%H:%M}-{s.end():%H:%M} {KIND_LABEL[s.kind]}: {s.exam}"
                + (f" ({s.topic})" if s.topic else "")
                for s in plan.sessions_on(day)
            )
            lines.append(f"- {day:%a %d.%m} - {blocks}")
    return "\n".join(lines) + "\n"


def weekly_hours(plan: Plan) -> dict[date, dict[str, float]]:
    weeks: dict[date, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for s in plan.sessions:
        monday = s.day - timedelta(days=s.day.weekday())
        weeks[monday][s.exam] += s.hours
    return weeks


def _ics_time(moment: datetime) -> str:
    return moment.strftime("%Y%m%dT%H%M%S")


def _event(
    uid: str, start: datetime, end: datetime, summary: str, tz: str, stamp: str,
    location: str = "", description: str = "",
) -> list[str]:
    extra = [f"DESCRIPTION:{_ics_escape(description)}"] if description else []
    return [
        "BEGIN:VEVENT",
        f"UID:{uid}@exam-schedule-system",
        f"DTSTAMP:{stamp}",
        f"DTSTART;TZID={tz}:{_ics_time(start)}",
        f"DTEND;TZID={tz}:{_ics_time(end)}",
        f"SUMMARY:{_ics_escape(summary)}",
        f"LOCATION:{_ics_escape(location)}",
        *extra,
        "END:VEVENT",
    ]


def _ics_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
        .replace("\r\n", "\\n").replace("\n", "\\n")
    )


def _fold(line: str) -> list[str]:
    """RFC 5545: lines longer than 75 octets continue on the next line after a space."""
    parts, current = [], ""
    for ch in line:
        limit = 75 if not parts else 74  # continuation lines start with a space
        if len((current + ch).encode("utf-8")) > limit:
            parts.append(current)
            current = ""
        current += ch
    parts.append(current)
    return [parts[0]] + [" " + p for p in parts[1:]]


def to_ics(plan: Plan, exams: list[Exam], timezone_name: str = "Europe/Helsinki") -> str:
    stamp = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//exam-schedule-system//EN", "CALSCALE:GREGORIAN"]
    for i, s in enumerate(plan.sessions):
        start = datetime.combine(s.day, s.start)
        end = start + timedelta(hours=s.hours)
        lines += _event(
            f"s{i}-{s.day:%Y%m%d}", start, end, f"{KIND_LABEL[s.kind]}: {s.exam}",
            timezone_name, stamp, description=s.topic or "",
        )
    for i, exam in enumerate(exams):
        if exam.starts_at():
            title = "EXAM" if exam.date_confirmed else "EXAM (date not confirmed)"
            lines += _event(
                f"e{i}-{exam.exam_date:%Y%m%d}", exam.starts_at(), exam.ends_at(),
                f"{title}: {exam.name}", timezone_name, stamp, str(exam.location),
            )
    lines.append("END:VCALENDAR")
    return "\r\n".join(folded for line in lines for folded in _fold(line)) + "\r\n"
