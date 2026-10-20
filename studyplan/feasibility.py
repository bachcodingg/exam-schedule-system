"""Check whether the estimated hours fit into the time available before each deadline."""

from __future__ import annotations

from .models import Exam, Profile
from .timeline import Day


def check(profile: Profile, exams: list[Exam], needed: dict[str, float], days: list[Day]) -> list[str]:
    warnings = []
    for deadline in sorted({e.exam_date for e in exams}):
        due = [e for e in exams if e.exam_date <= deadline]
        need = sum(needed[e.name] for e in due)
        available = sum(d.hours for d in days if d.date < deadline and d.kind in ("study", "review"))
        if need <= available:
            continue
        shortfall = need - available
        study_days = sum(1 for d in days if d.date < deadline and d.kind in ("study", "review"))
        extra_min = 60 * shortfall / max(study_days, 1)
        names = ", ".join(e.name for e in due)
        warnings.append(
            f"Not enough time before {deadline:%d.%m}: {need:.0f} h needed for {names}, "
            f"only {available:.0f} h available ({shortfall:.0f} h short). Options: study "
            f"{extra_min:.0f} more min/day, start earlier, use buffer days, or lower a target grade."
        )
    first = min(e.exam_date for e in exams)
    if profile.start_date >= first:
        warnings.append(f"Start date {profile.start_date} is not before the first exam ({first}).")
    return warnings
