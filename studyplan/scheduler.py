"""Greedy least-slack scheduler.

1. Review days (the day before an exam) are reserved for that exam.
2. One mock exam per exam is placed on the last study day before its review day,
   at the real exam start time.
3. Every other study block goes to the exam with the highest urgency
   (remaining hours / study hours left before it), and the two blocks of a day
   go to different exams whenever possible (interleaving).
4. Time left over after all estimates are met becomes extra practice for the
   exam that is least ahead of its estimate.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from . import feasibility, timeline
from .models import Exam, Plan, Profile, Session

MOCK_SEARCH_DAYS = 10  # how far before the exam to look for a mock-exam day
CRUNCH_URGENCY = 0.9  # above this an exam may take both blocks of a day
BREAK_HOURS = 0.5


def schedule(profile: Profile, exams: list[Exam], needed: dict[str, float]) -> Plan:
    days = timeline.build(profile, exams)
    by_name = {e.name: e for e in exams}
    remaining = dict(needed)
    picks: dict[date, list[tuple[str, str, float]]] = {}  # day -> [(exam, kind, hours)]

    # 1. Review days.
    for day in days:
        if day.kind == "review":
            picks[day.date] = []
            for i, hours in enumerate(day.blocks):
                name = day.exams[i % len(day.exams)]
                picks[day.date].append((name, "review", hours))
                remaining[name] -= hours

    study_days = [d for d in days if d.kind == "study"]

    # 2. Mock exams.
    mocks: dict[date, list[str]] = {}
    for exam in sorted(exams, key=lambda e: e.exam_date):
        for day in reversed(study_days):
            too_late = day.date >= exam.exam_date - timedelta(days=1)
            too_early = day.date < exam.exam_date - timedelta(days=MOCK_SEARCH_DAYS)
            if too_late or too_early or len(mocks.get(day.date, [])) >= len(day.blocks):
                continue
            mocks.setdefault(day.date, []).append(exam.name)
            break

    def urgency(name: str, today: date) -> float:
        left = timeline.study_hours_between(days, today, by_name[name].exam_date - timedelta(days=1))
        return remaining[name] / left if left > 0 else float("inf")

    # 3. Regular blocks.
    for day in study_days:
        chosen: list[tuple[str, str, float]] = []
        open_blocks = list(day.blocks)
        for name in mocks.get(day.date, []):
            hours = open_blocks.pop(0)
            chosen.append((name, "mock", hours))
            remaining[name] -= hours
        for hours in open_blocks:
            candidates = [
                n for n in remaining
                if remaining[n] > 0.01 and day.date < by_name[n].exam_date - timedelta(days=1)
            ]
            if not candidates:
                chosen.append(("", "free", hours))
                continue
            ranked = sorted(candidates, key=lambda n: (-urgency(n, day.date), by_name[n].exam_date))
            used = {c[0] for c in chosen}
            fresh = [n for n in ranked if n not in used]
            best = ranked[0]
            if fresh and (best in used and urgency(best, day.date) < CRUNCH_URGENCY):
                best = fresh[0]
            chosen.append((best, "learn", hours))
            remaining[best] -= hours
        picks[day.date] = chosen

    # 4. Fill free blocks with practice.
    if profile.fill_free_time:
        _fill_free_blocks(picks, exams, needed)

    warnings = feasibility.check(profile, exams, needed, days)
    for name, left in remaining.items():
        if left > 0.5:
            warnings.append(f"{name}: {left:.1f} h of the estimate could not be scheduled.")

    sessions = []
    for day in days:
        sessions.extend(_place(day.date, picks.get(day.date, []), by_name, profile))

    scheduled = {e.name: 0.0 for e in exams}
    for s in sessions:
        scheduled[s.exam] += s.hours
    return Plan(sessions, dict(needed), scheduled, {d.date: d.kind for d in days}, warnings)


def _fill_free_blocks(picks: dict[date, list[tuple[str, str, float]]], exams: list[Exam], needed: dict[str, float]) -> None:
    totals = {e.name: 0.0 for e in exams}
    for chosen in picks.values():
        for name, kind, hours in chosen:
            if name:
                totals[name] += hours
    for day in sorted(picks):
        chosen = picks[day]
        for i, (name, kind, hours) in enumerate(chosen):
            if kind != "free":
                continue
            used = {c[0] for c in chosen}
            open_exams = [e for e in exams if day < e.exam_date - timedelta(days=1)]
            if not open_exams:
                continue
            # The exam whose plan is least ahead of its estimate, preferring one not already today.
            pick = min(open_exams, key=lambda e: (e.name in used, totals[e.name] / max(needed[e.name], 1)))
            chosen[i] = (pick.name, "practice", hours)
            totals[pick.name] += hours


def _place(day: date, chosen: list[tuple[str, str, float]], by_name: dict[str, Exam], profile: Profile) -> list[Session]:
    """Give each block a start time. Mocks start at the real exam time when it is known."""
    sessions = []
    busy: list[tuple[datetime, datetime]] = []
    for name, kind, hours in chosen:
        exam = by_name.get(name)
        if kind == "mock" and exam and exam.start:
            start = datetime.combine(day, exam.start)
            # Exams sharing a slot get back-to-back mocks.
            for b_start, b_end in sorted(busy):
                if b_start <= start < b_end:
                    start = b_end
            sessions.append(Session(day, start.time(), hours, name, kind))
            busy.append((start, start + timedelta(hours=hours)))
    cursor = datetime.combine(day, profile.day_start)
    for name, kind, hours in chosen:
        exam = by_name.get(name)
        if not name or (kind == "mock" and exam and exam.start):
            continue
        end = cursor + timedelta(hours=hours)
        for b_start, b_end in sorted(busy):
            if cursor < b_end and b_start < end:
                cursor = b_end + timedelta(hours=BREAK_HOURS)
                end = cursor + timedelta(hours=hours)
        sessions.append(Session(day, cursor.time(), hours, name, kind))
        busy.append((cursor, end))
        cursor = end + timedelta(hours=BREAK_HOURS)
    return sessions
