"""Greedy least-slack scheduler.

1. Review days (the day before an exam) are reserved for that exam.
2. `exam.mocks` mock exams per exam are placed on the last study days before its
   review day, MOCK_GAP_DAYS apart, at the real exam start time.
3. Every other study block goes to the exam with the highest urgency
   (remaining hours / study hours left before it), and the two blocks of a day
   go to different exams whenever possible (interleaving).
4. Time left over after all estimates are met becomes extra practice for the
   exam that is least ahead of its estimate.
5. Learn sessions are labelled with the exam's topics in order, split by weight.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from . import feasibility, timeline
from .models import Exam, Plan, Profile, Session

MOCK_SEARCH_DAYS = 10  # how far before the exam to look for a mock-exam day
CRUNCH_URGENCY = 0.9  # above this an exam may take both blocks of a day
BREAK_HOURS = 0.5
MOCK_GAP_DAYS = 2  # at least this many days between two mocks of the same exam
TOPIC_MIN_HOURS = 0.5  # a topic is named on a session if it fills this much of it
SESSION_TOPIC = {
    "review": "formula sheet, mistakes log, one timed problem per topic",
    "mock": "full past exam, timed, closed book, then mark it",
    "practice": "mixed past-exam problems, weakest topics first",
}


def schedule(profile: Profile, exams: list[Exam], needed: dict[str, float]) -> Plan:
    days = timeline.build(profile, exams)
    by_name = {e.name: e for e in exams}
    reviews = timeline.review_dates(days)
    # Last date on which an exam can still get study blocks (its review day is exclusive).
    cutoff = {e.name: reviews.get(e.name, e.exam_date - timedelta(days=1)) for e in exams}
    remaining = dict(needed)
    picks: dict[date, list[tuple[str, str, float]]] = {}  # day -> [(exam, kind, hours)]
    warnings_early: list[str] = []

    # 1. Review days.
    for day in days:
        if day.kind == "review":
            picks[day.date] = []
            for i, hours in enumerate(day.blocks):
                name = day.exams[i % len(day.exams)]
                picks[day.date].append((name, "review", hours))
                remaining[name] -= hours

    study_days = [d for d in days if d.kind == "study"]

    # 2. Mock exams, the last one as close to the exam as possible, earlier ones spaced out.
    mocks: dict[date, list[str]] = {}
    for exam in sorted(exams, key=lambda e: e.exam_date):
        search_days = MOCK_SEARCH_DAYS + MOCK_GAP_DAYS * (exam.mocks - 1)
        placed: list[date] = []
        for day in reversed(study_days):
            if len(placed) >= exam.mocks:
                break
            too_late = day.date >= cutoff[exam.name]
            too_early = day.date < exam.exam_date - timedelta(days=search_days)
            too_close = any(abs((day.date - p).days) < MOCK_GAP_DAYS for p in placed)
            if too_late or too_early or too_close or len(mocks.get(day.date, [])) >= len(day.blocks):
                continue
            mocks.setdefault(day.date, []).append(exam.name)
            placed.append(day.date)
        if len(placed) < exam.mocks:
            warnings_early.append(f"{exam.name}: only {len(placed)} of {exam.mocks} mock exams fit.")

    def urgency(name: str, today: date) -> float:
        left = timeline.study_hours_between(days, today, cutoff[name])
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
                if remaining[n] > 0.01 and day.date < cutoff[n]
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
        _fill_free_blocks(picks, exams, needed, cutoff)

    warnings = feasibility.check(profile, exams, needed, days) + warnings_early
    for name, left in remaining.items():
        if left > 0.5:
            warnings.append(f"{name}: {left:.1f} h of the estimate could not be scheduled.")

    sessions = []
    for day in days:
        sessions.extend(_place(day.date, picks.get(day.date, []), by_name, profile))
    _label_topics(sessions, exams)

    scheduled = {e.name: 0.0 for e in exams}
    for s in sessions:
        scheduled[s.exam] += s.hours
    return Plan(sessions, dict(needed), scheduled, {d.date: d.kind for d in days}, warnings)


def _fill_free_blocks(
    picks: dict[date, list[tuple[str, str, float]]],
    exams: list[Exam],
    needed: dict[str, float],
    cutoff: dict[str, date],
) -> None:
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
            open_exams = [e for e in exams if day < cutoff[e.name]]
            if not open_exams:
                continue
            # The exam whose plan is least ahead of its estimate, preferring one not already today.
            pick = min(open_exams, key=lambda e: (e.name in used, totals[e.name] / max(needed[e.name], 1)))
            chosen[i] = (pick.name, "practice", hours)
            totals[pick.name] += hours


def _label_topics(sessions: list[Session], exams: list[Exam]) -> None:
    """Walk each exam's learn sessions in date order and split them over its topics by weight.

    Practice sessions get a second round over the same topics (spaced repetition).
    A session gets every topic that covers at least TOPIC_MIN_HOURS of it, so a short topic
    is never skipped. Review and mock sessions get a fixed description.
    """
    ordered = sorted(sessions, key=lambda s: (s.day, s.start))
    for s in ordered:
        s.topic = SESSION_TOPIC.get(s.kind)
    for exam in exams:
        if not exam.topics:
            continue
        for kind in ("learn", "practice"):
            _split_over_topics([s for s in ordered if s.exam == exam.name and s.kind == kind], exam)


def _split_over_topics(sessions: list[Session], exam: Exam) -> None:
    total = sum(s.hours for s in sessions)
    weights = sum(t.weight for t in exam.topics)
    spans, begin = [], 0.0
    for t in exam.topics:
        end = begin + total * t.weight / weights
        spans.append((begin, end, t.name))
        begin = end
    done = 0.0
    for s in sessions:
        covered = []
        for b, e, name in spans:
            overlap = min(e, done + s.hours) - max(b, done)
            if overlap > 1e-9 and overlap >= min(TOPIC_MIN_HOURS, e - b) - 1e-9:
                covered.append(name)
        s.topic = " + ".join(covered) or spans[-1][2]
        done += s.hours


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
