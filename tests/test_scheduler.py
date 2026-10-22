from datetime import date, time, timedelta
from pathlib import Path

from studyplan import estimator, scheduler, timeline
from studyplan.models import Exam, Location, Profile, Topic, load

DATA = Path(__file__).parent.parent / "data" / "exams_lut_2026.json"


def lut_plan():
    profile, exams = load(DATA)
    needed = {e.name: estimator.estimate(e).hours for e in exams}
    return profile, exams, scheduler.schedule(profile, exams, needed)


def test_timeline_marks_review_exam_and_buffer_days():
    profile, exams = load(DATA)
    kinds = {d.date: d.kind for d in timeline.build(profile, exams)}
    assert kinds[date(2026, 11, 30)] == "exam"
    assert kinds[date(2026, 11, 29)] == "review"  # a Sunday, but the exam is the next day
    assert kinds[date(2026, 10, 25)] == "buffer"
    assert kinds[date(2026, 10, 21)] == "study"


def test_never_studies_for_an_exam_after_it_happened():
    _, exams, plan = lut_plan()
    dates = {e.name: e.exam_date for e in exams}
    assert all(s.day < dates[s.exam] for s in plan.sessions)


def test_daily_hours_are_respected():
    profile, _, plan = lut_plan()
    for day in plan.day_kinds:
        assert sum(s.hours for s in plan.sessions_on(day)) <= profile.daily_hours


def test_review_day_only_reviews_the_next_exams():
    _, _, plan = lut_plan()
    review = plan.sessions_on(date(2026, 11, 29))
    assert {s.exam for s in review} == {"Integral Calculus", "Statistics II"}
    assert all(s.kind == "review" for s in review)


def test_mocks_at_real_exam_time_and_shared_slot_back_to_back():
    _, _, plan = lut_plan()
    mocks = [s for s in plan.sessions_on(date(2026, 11, 28)) if s.kind == "mock"]
    assert sorted(s.start for s in mocks) == [time(16, 30), time(18, 30)]


def test_nov_30_exams_get_their_estimate():
    _, _, plan = lut_plan()
    for name in ("Integral Calculus", "Statistics II"):
        assert plan.scheduled[name] >= plan.needed[name]


def test_shortfall_is_reported():
    start = date(2026, 11, 23)
    profile = Profile(home_city="Lappeenranta", start_date=start, daily_hours=2)
    exam = Exam("Huge", 10, Location("LUT", "Lappeenranta"), date=start + timedelta(days=5))
    plan = scheduler.schedule(profile, [exam], {"Huge": 100})
    assert any("Not enough time" in w for w in plan.warnings)


def three_exams(**extra):
    profile = Profile(home_city="Lappeenranta", start_date=date(2026, 11, 2))
    lut = Location("LUT", "Lappeenranta")
    exams = [
        Exam("A", 3, lut, date=date(2026, 11, 30), start=time(16, 30), **extra),
        Exam("B", 3, lut, date=date(2026, 12, 1), **extra),
    ]
    return profile, exams


def test_back_to_back_exam_gets_an_earlier_review_day():
    profile, exams = three_exams()
    days = {d.date: d for d in timeline.build(profile, exams)}
    assert days[date(2026, 11, 29)].exams == ["A"]
    assert days[date(2026, 11, 28)].kind == "review" and days[date(2026, 11, 28)].exams == ["B"]
    plan = scheduler.schedule(profile, exams, {"A": 10, "B": 10})
    assert not [s for s in plan.sessions if s.exam == "B" and s.day > date(2026, 11, 28)]


def test_several_mocks_are_spaced_out():
    profile, exams = three_exams(mocks=3)
    plan = scheduler.schedule(profile, exams, {"A": 10, "B": 10})
    days = sorted(s.day for s in plan.sessions if s.exam == "A" and s.kind == "mock")
    assert len(days) == 3
    assert all((b - a).days >= scheduler.MOCK_GAP_DAYS for a, b in zip(days, days[1:]))
    assert all(s.start == time(16, 30) for s in plan.sessions if s.exam == "A" and s.kind == "mock")


def test_topics_follow_their_order_and_weight():
    profile, exams = three_exams()
    exams[0].topics = [Topic("first", 1), Topic("big", 3)]
    plan = scheduler.schedule(profile, exams, {"A": 16, "B": 10})
    learn = sorted((s for s in plan.sessions if s.exam == "A" and s.kind == "learn"), key=lambda s: s.day)
    assert learn[0].topic == "first"
    assert learn[-1].topic == "big"
    big = sum(s.hours for s in learn if s.topic == "big")
    first = sum(s.hours for s in learn if s.topic == "first")
    assert big > 2 * first
    practice = [s for s in plan.sessions if s.exam == "A" and s.kind == "practice"]
    assert practice and all(s.topic in ("first", "big", "first + big") for s in practice)
