"""Turn the date range into typed days: study, review, exam, buffer or blocked."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from .models import Exam, Profile


@dataclass
class Day:
    date: date
    kind: str  # study | review | exam | buffer | blocked
    blocks: list[float] = field(default_factory=list)  # focus block lengths in hours
    exams: list[str] = field(default_factory=list)  # exams held (exam) or reviewed (review)

    @property
    def hours(self) -> float:
        return sum(self.blocks)


def build(profile: Profile, exams: list[Exam]) -> list[Day]:
    """One Day per date from the start date up to and including the last exam.

    Rules: no studying on exam days, the last free day before an exam is review-only
    (even if it is a rest weekday), rest weekdays become buffer days. When the day before
    an exam is itself an exam day or another exam's review day, the review moves earlier.
    """
    by_date: dict[date, list[str]] = {}
    for exam in exams:
        by_date.setdefault(exam.exam_date, []).append(exam.name)

    review_on: dict[date, list[str]] = {}
    for exam_day in sorted(by_date):
        current = exam_day - timedelta(days=1)
        while current in by_date or current in review_on or current in profile.blocked_dates:
            current -= timedelta(days=1)
        if current >= profile.start_date:
            review_on[current] = by_date[exam_day]

    last = max(by_date)
    blocks = profile.block_lengths()
    days = []
    current = profile.start_date
    while current <= last:
        if current in by_date:
            day = Day(current, "exam", exams=by_date[current])
        elif current in profile.blocked_dates:
            day = Day(current, "blocked")
        elif current in review_on:
            day = Day(current, "review", list(blocks), review_on[current])
        elif current.weekday() in profile.rest_weekdays:
            day = Day(current, "buffer")
        else:
            day = Day(current, "study", list(blocks))
        days.append(day)
        current += timedelta(days=1)
    return days


def review_dates(days: list[Day]) -> dict[str, date]:
    """Exam name -> its review day. Study for that exam must stop before this date."""
    return {name: d.date for d in days if d.kind == "review" for name in d.exams}


def study_hours_between(days: list[Day], start: date, end: date) -> float:
    """Study-day hours in [start, end)."""
    return sum(d.hours for d in days if d.kind == "study" and start <= d.date < end)
