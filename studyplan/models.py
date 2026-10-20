"""Core data structures: exams, the student profile, and the generated plan."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path

CATEGORIES = (
    "math_proof",
    "math_computational",
    "statistics",
    "programming",
    "conceptual",
    "memorization",
)

WEEKDAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}


@dataclass
class Location:
    university: str
    city: str
    campus: str | None = None

    def __str__(self) -> str:
        return f"{self.university} {self.campus or self.city}"


@dataclass
class Exam:
    name: str
    credits: float
    location: Location
    date: date | None = None
    start: time | None = None
    duration_h: float = 3.0
    category: str = "conceptual"
    difficulty: int = 3  # 1 (easy) .. 5 (very hard)
    prior_knowledge: float = 0.0  # 0.0 .. 1.0
    target: str = "good"  # pass | good | top
    documents: list[str] = field(default_factory=list)
    assumed_date: date | None = None  # used while the real date is unknown
    hours: float | None = None  # manual override of the estimate

    def __post_init__(self) -> None:
        if self.category not in CATEGORIES:
            raise ValueError(f"{self.name}: unknown category {self.category!r}")
        if self.date is None and self.assumed_date is None:
            raise ValueError(f"{self.name}: needs either 'date' or 'assumed_date'")

    @property
    def exam_date(self) -> date:
        return self.date or self.assumed_date  # type: ignore[return-value]

    @property
    def date_confirmed(self) -> bool:
        return self.date is not None

    def starts_at(self) -> datetime | None:
        if self.start is None:
            return None
        return datetime.combine(self.exam_date, self.start)

    def ends_at(self) -> datetime | None:
        begin = self.starts_at()
        return begin + timedelta(hours=self.duration_h) if begin else None


@dataclass
class Profile:
    home_city: str
    start_date: date
    daily_hours: float = 4.0
    block_hours: float = 2.0
    day_start: time = time(9, 0)
    rest_weekdays: list[int] = field(default_factory=lambda: [6])
    blocked_dates: list[date] = field(default_factory=list)
    fill_free_time: bool = True

    def block_lengths(self) -> list[float]:
        """Split the daily hours into focus blocks, e.g. 4h -> [2, 2], 3h -> [2, 1]."""
        blocks, left = [], self.daily_hours
        while left > 1e-9:
            blocks.append(min(self.block_hours, left))
            left -= self.block_hours
        return blocks


@dataclass
class Session:
    day: date
    start: time
    hours: float
    exam: str
    kind: str  # learn | review | mock | practice

    def end(self) -> time:
        return (datetime.combine(self.day, self.start) + timedelta(hours=self.hours)).time()


@dataclass
class Plan:
    sessions: list[Session]
    needed: dict[str, float]  # estimated hours per exam
    scheduled: dict[str, float]  # hours actually placed in the calendar
    day_kinds: dict[date, str]  # study | review | exam | buffer | blocked
    warnings: list[str] = field(default_factory=list)

    def sessions_on(self, day: date) -> list[Session]:
        return sorted((s for s in self.sessions if s.day == day), key=lambda s: s.start)


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _parse_time(value: str | None) -> time | None:
    return time.fromisoformat(value) if value else None


def _parse_weekday(value: int | str) -> int:
    return value if isinstance(value, int) else WEEKDAYS[value.lower()[:3]]


def load(path: str | Path) -> tuple[Profile, list[Exam]]:
    """Read a JSON input file (see data/exams_lut_2026.json)."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    s = raw["student"]
    profile = Profile(
        home_city=s["home_city"],
        start_date=date.fromisoformat(s["start_date"]),
        daily_hours=s.get("daily_hours", 4.0),
        block_hours=s.get("block_hours", 2.0),
        day_start=_parse_time(s.get("day_start")) or time(9, 0),
        rest_weekdays=[_parse_weekday(d) for d in s.get("rest_weekdays", ["sun"])],
        blocked_dates=[date.fromisoformat(d) for d in s.get("blocked_dates", [])],
        fill_free_time=s.get("fill_free_time", True),
    )
    exams = [
        Exam(
            name=e["name"],
            credits=e["credits"],
            location=Location(e["university"], e["city"], e.get("campus")),
            date=_parse_date(e.get("date")),
            start=_parse_time(e.get("start")),
            duration_h=e.get("duration_h", 3.0),
            category=e.get("category", "conceptual"),
            difficulty=e.get("difficulty", 3),
            prior_knowledge=e.get("prior_knowledge", 0.0),
            target=e.get("target", "good"),
            documents=e.get("documents", []),
            assumed_date=_parse_date(e.get("assumed_date")),
            hours=e.get("hours"),
        )
        for e in raw["exams"]
    ]
    return profile, exams
