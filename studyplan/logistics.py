"""Exam-day logistics: shared slots, travel between cities and early exams away from home."""

from __future__ import annotations

from datetime import time, timedelta
from itertools import combinations

from .models import Exam, Profile

# Approximate door-to-door travel time in hours (train). Extend as needed.
TRAVEL_HOURS = {
    frozenset({"Lappeenranta", "Lahti"}): 1.75,
    frozenset({"Lappeenranta", "Helsinki"}): 2.25,
    frozenset({"Lahti", "Helsinki"}): 1.0,
}
SAFETY_MARGIN_H = 1.0
EARLY_EXAM_HOUR = 10


_TRAVEL_LOWER = {frozenset(c.lower() for c in pair): h for pair, h in TRAVEL_HOURS.items()}


def travel_hours(a: str, b: str) -> float | None:
    """Hours between two cities, ignoring case and surrounding spaces; None if unknown."""
    a, b = a.strip().lower(), b.strip().lower()
    if a == b:
        return 0.0
    return _TRAVEL_LOWER.get(frozenset({a, b}))


def check(profile: Profile, exams: list[Exam]) -> list[str]:
    notes = []

    for exam in exams:
        if not exam.date_confirmed:
            notes.append(
                f"{exam.name}: date not confirmed, planning with {exam.assumed_date:%d.%m}. "
                "Update the input file when it is announced and re-run."
            )
        elif exam.start is None:
            notes.append(
                f"{exam.name}: start time unknown, so its mock runs in a normal study block. "
                "Add 'start' when it is announced and re-run."
            )

    slots: dict[tuple, list[Exam]] = {}
    for exam in exams:
        if exam.start:
            slots.setdefault((exam.exam_date, exam.start), []).append(exam)
    for (day, start), group in slots.items():
        if len(group) > 1:
            total = sum(e.credits for e in group)
            split = ", ".join(
                f"{e.name} ~{60 * e.duration_h * e.credits / total:.0f} min" for e in group
            )
            notes.append(
                f"{day:%d.%m} {start:%H:%M}: {len(group)} exams share one slot. "
                f"Suggested time split by credits: {split}. Rehearse it in the mock."
            )

    for a, b in combinations(sorted(exams, key=lambda e: (e.exam_date, e.start or time.min)), 2):
        if a.exam_date != b.exam_date or not (a.start and b.start) or a.start == b.start:
            continue
        travel = travel_hours(a.location.city, b.location.city)
        gap = (b.starts_at() - a.ends_at()).total_seconds() / 3600
        where = f"{a.location.city} -> {b.location.city}"
        if travel is None:
            notes.append(f"{a.exam_date:%d.%m}: {a.name} then {b.name} ({where}); travel time unknown, check it.")
        elif gap < travel + SAFETY_MARGIN_H:
            notes.append(
                f"CONFLICT {a.exam_date:%d.%m}: {a.name} ends {a.ends_at():%H:%M}, {b.name} starts "
                f"{b.start:%H:%M} ({where}, ~{travel:g} h travel). Ask about another exam date or place."
            )
        else:
            leave = a.ends_at() + timedelta(minutes=15)
            arrive = leave + timedelta(hours=travel)
            notes.append(
                f"{a.exam_date:%d.%m} double exam day: {a.name} in {a.location.city} until "
                f"{a.ends_at():%H:%M}, leave ~{leave:%H:%M}, arrive {b.location.city} ~{arrive:%H:%M}, "
                f"{b.name} at {b.start:%H:%M}. Ask whether {a.name} can be taken in {b.location.city}."
            )

    for exam in exams:
        away = travel_hours(exam.location.city, profile.home_city) != 0.0
        if away and exam.start and exam.start.hour < EARLY_EXAM_HOUR:
            travel = travel_hours(profile.home_city, exam.location.city)
            eta = f"~{travel:g} h" if travel else "unknown time"
            notes.append(
                f"{exam.name} starts {exam.start:%H:%M} in {exam.location.city} ({eta} from "
                f"{profile.home_city}): travel the evening before and stay overnight."
            )
    return notes
