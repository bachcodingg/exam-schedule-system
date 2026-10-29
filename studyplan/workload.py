"""Workload in days: what an estimate means for the calendar.

50 h at 3 h/day is 17 study days. Next to that pace figure the analysis shows the study days
the calendar really has before the exam, what the plan gives the exam, and the latest start
date that still fits every estimate.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

from . import timeline
from .models import Exam, Plan, Profile
from .timeline import Day


@dataclass
class ExamLoad:
    exam: str
    hours: float  # estimated
    pace_days: int  # study days at the daily hours if this were the only exam
    study_days: int  # study days before the exam's review day, plus the review day
    planned_hours: float
    planned_days: int  # days with at least one session for this exam
    by_kind: dict[str, float] = field(default_factory=dict)  # learn | practice | mock | review
    first: date | None = None
    last: date | None = None


@dataclass
class Workload:
    daily_hours: float
    exams: list[ExamLoad]
    total_hours: float
    capacity: float  # study and review hours up to the last exam
    latest_start: date | None  # None: the estimates do not fit even from the start date
    start: date

    @property
    def slack_days(self) -> int | None:
        return (self.latest_start - self.start).days if self.latest_start else None


def latest_start(days: list[Day], exams: list[Exam], needed: dict[str, float]) -> date | None:
    """The latest first study day from which every deadline's cumulative hours still fit."""
    latest = None
    for deadline in sorted({e.exam_date for e in exams}):
        need = sum(needed[e.name] for e in exams if e.exam_date <= deadline)
        hours, start = 0.0, None
        for d in reversed([d for d in days if d.date < deadline and d.kind in ("study", "review")]):
            hours += d.hours
            if hours >= need - 1e-9:
                start = d.date
                break
        if start is None and need > 1e-9:
            return None
        if start is not None:
            latest = start if latest is None else min(latest, start)
    return latest


def analyse(profile: Profile, exams: list[Exam], plan: Plan) -> Workload:
    days = timeline.build(profile, exams)
    reviews = timeline.review_dates(days)
    loads = []
    for exam in sorted(exams, key=lambda e: e.exam_date):
        sessions = [s for s in plan.sessions if s.exam == exam.name]
        by_kind: dict[str, float] = {}
        for s in sessions:
            by_kind[s.kind] = by_kind.get(s.kind, 0.0) + s.hours
        cutoff = reviews.get(exam.name, exam.exam_date)
        study_days = sum(1 for d in days if d.kind == "study" and d.date < cutoff)
        hours = plan.needed[exam.name]
        loads.append(ExamLoad(
            exam=exam.name,
            hours=hours,
            pace_days=math.ceil(hours / profile.daily_hours - 1e-9) if profile.daily_hours else 0,
            study_days=study_days + (exam.name in reviews),
            planned_hours=sum(by_kind.values()),
            planned_days=len({s.day for s in sessions}),
            by_kind=by_kind,
            first=min((s.day for s in sessions), default=None),
            last=max((s.day for s in sessions), default=None),
        ))
    return Workload(
        daily_hours=profile.daily_hours,
        exams=loads,
        total_hours=sum(plan.needed.values()),
        capacity=sum(d.hours for d in days if d.kind in ("study", "review")),
        latest_start=latest_start(days, exams, plan.needed),
        start=profile.start_date,
    )


def summary(load: ExamLoad, daily_hours: float) -> str:
    """One sentence, e.g. '50 h at 3 h/day is 17 study days; the calendar has 26 before the exam.'"""
    return (
        f"{load.hours:g} h at {daily_hours:g} h/day is {load.pace_days} study days; "
        f"the calendar has {load.study_days} before the exam"
    )


def to_markdown(work: Workload) -> list[str]:
    lines = [
        f"| Exam | Estimated h | Alone at {work.daily_hours:g} h/day | Study days before it "
        "| Planned h | Days with sessions |",
        "|---|---|---|---|---|---|",
    ]
    for load in work.exams:
        lines.append(
            f"| {load.exam} | {load.hours:g} | {load.pace_days} days | {load.study_days} | "
            f"{load.planned_hours:g} | {load.planned_days} |"
        )
    lines.append("")
    total = f"All exams together: {work.total_hours:g} h estimated, {work.capacity:g} h of study time in the calendar."
    if work.latest_start is None:
        total += " The estimates do not fit even from today: see the warnings."
    elif work.slack_days == 0:
        total += f" There is no slack: every study day from {work.start:%d.%m} on is needed."
    else:
        total += (
            f" Latest start that still fits every estimate: {work.latest_start:%a %d.%m} "
            f"({work.slack_days} days of slack). The extra time becomes spaced practice."
        )
    lines.append(total)
    return lines
