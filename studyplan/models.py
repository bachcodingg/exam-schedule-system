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
TARGETS = ("pass", "good", "top")


class InputError(ValueError):
    """The input file is missing a field or has a value out of range."""


@dataclass
class Location:
    university: str
    city: str
    campus: str | None = None

    def __str__(self) -> str:
        return f"{self.university} {self.campus or self.city}"


@dataclass
class Topic:
    name: str
    weight: float = 1.0  # share of the study time, e.g. typical exam points


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
    topics: list[Topic] = field(default_factory=list)  # study order, weighted by exam points
    mocks: int = 1  # timed mock exams, e.g. one per past exam you have

    def __post_init__(self) -> None:
        problems = []
        if self.category not in CATEGORIES:
            problems.append(f"unknown category {self.category!r}, use one of {', '.join(CATEGORIES)}")
        if self.date is None and self.assumed_date is None:
            problems.append("needs either 'date' or 'assumed_date'")
        if self.credits <= 0:
            problems.append(f"credits must be positive, got {self.credits}")
        if self.difficulty not in range(1, 6):
            problems.append(f"difficulty must be 1..5, got {self.difficulty}")
        if not 0 <= self.prior_knowledge <= 1:
            problems.append(f"prior_knowledge must be 0.0..1.0, got {self.prior_knowledge}")
        if self.target not in TARGETS:
            problems.append(f"target must be one of {', '.join(TARGETS)}, got {self.target!r}")
        if self.duration_h <= 0:
            problems.append(f"duration_h must be positive, got {self.duration_h}")
        if self.mocks < 0:
            problems.append(f"mocks cannot be negative, got {self.mocks}")
        if self.hours is not None and self.hours < 0:
            problems.append(f"hours cannot be negative, got {self.hours}")
        if any(t.weight <= 0 for t in self.topics):
            problems.append("topic weights must be positive")
        if problems:
            raise InputError(f"{self.name}: " + "; ".join(problems))

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
    timezone: str = "Europe/Helsinki"  # used for the .ics calendar

    def __post_init__(self) -> None:
        if self.block_hours <= 0:
            raise InputError(f"block_hours must be positive, got {self.block_hours}")
        if not 0 <= self.daily_hours <= 24:
            raise InputError(f"daily_hours must be 0..24, got {self.daily_hours}")

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
    topic: str | None = None

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
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        raise InputError(f"invalid date {value!r}, use YYYY-MM-DD") from None


def _parse_time(value: str | None) -> time | None:
    try:
        return time.fromisoformat(value) if value else None
    except ValueError:
        raise InputError(f"invalid time {value!r}, use HH:MM") from None


def _parse_weekday(value: int | str) -> int:
    if isinstance(value, int) and 0 <= value <= 6:
        return value
    if isinstance(value, str) and value.lower()[:3] in WEEKDAYS:
        return WEEKDAYS[value.lower()[:3]]
    raise InputError(f"invalid weekday {value!r}, use mon..sun")


def _parse_topic(value: str | dict) -> Topic:
    if isinstance(value, str):
        return Topic(value)
    return Topic(value["name"], value.get("weight", 1.0))


def load(path: str | Path) -> tuple[Profile, list[Exam]]:
    """Read a JSON input file (see data/exams_lut_2026.json)."""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise InputError(f"{path} is not valid JSON: {err}") from None
    try:
        return _from_dict(raw)
    except KeyError as err:
        raise InputError(f"missing required field {err.args[0]!r}") from None


def _from_dict(raw: dict) -> tuple[Profile, list[Exam]]:
    s = raw["student"]
    profile = Profile(
        home_city=s["home_city"],
        start_date=_parse_date(s["start_date"]),
        daily_hours=s.get("daily_hours", 4.0),
        block_hours=s.get("block_hours", 2.0),
        day_start=_parse_time(s.get("day_start")) or time(9, 0),
        rest_weekdays=[_parse_weekday(d) for d in s.get("rest_weekdays", ["sun"])],
        blocked_dates=[_parse_date(d) for d in s.get("blocked_dates", [])],
        fill_free_time=s.get("fill_free_time", True),
        timezone=s.get("timezone", "Europe/Helsinki"),
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
            topics=[_parse_topic(t) for t in e.get("topics", [])],
            mocks=e.get("mocks", 1),
        )
        for e in raw["exams"]
    ]
    return profile, exams
