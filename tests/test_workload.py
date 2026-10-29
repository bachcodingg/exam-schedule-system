from datetime import date

from studyplan import scheduler, workload
from studyplan.models import Exam, Location, Profile

LUT = Location("LUT", "Lappeenranta")


def single(hours: float, daily: float, start=date(2026, 11, 2), exam_day=date(2026, 11, 30)):
    profile = Profile("Lappeenranta", start, daily_hours=daily, block_hours=1.5, rest_weekdays=[6])
    exams = [Exam("Integral Calculus", 3, LUT, date=exam_day, hours=hours)]
    plan = scheduler.schedule(profile, exams, {"Integral Calculus": hours})
    return workload.analyse(profile, exams, plan)


def test_fifty_hours_at_three_a_day_is_seventeen_days():
    work = single(50, 3)
    load = work.exams[0]
    assert load.pace_days == 17
    assert workload.summary(load, 3).startswith("50 h at 3 h/day is 17 study days")


def test_latest_start_leaves_exactly_enough_study_time():
    work = single(50, 3)
    assert work.latest_start is not None and work.slack_days > 0
    late = single(50, 3, start=work.latest_start)
    assert late.capacity >= 50
    too_late = single(50, 3, start=date(2026, 11, 20))
    assert too_late.latest_start is None


def test_two_deadlines_count_cumulatively():
    profile = Profile("Lappeenranta", date(2026, 11, 2), daily_hours=2, block_hours=2, rest_weekdays=[])
    exams = [
        Exam("A", 3, LUT, date=date(2026, 11, 10), hours=10),
        Exam("B", 3, LUT, date=date(2026, 11, 20), hours=24),
    ]
    plan = scheduler.schedule(profile, exams, {"A": 10, "B": 24})
    work = workload.analyse(profile, exams, plan)
    # A alone could start on 5.11 and B alone on 7.11, but together they need 17 days of
    # 2 h before 20.11, and only 2.11-9.11 and 11.11-19.11 are free: no day to spare.
    assert work.latest_start == date(2026, 11, 2) and work.slack_days == 0
    assert "no slack" in " ".join(workload.to_markdown(work))
