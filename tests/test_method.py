from datetime import date, time
from pathlib import Path

from studyplan import estimator, method, scheduler
from studyplan.models import Exam, Location, Plan, Session, Topic, load

DEMO = Path(__file__).parent.parent / "data" / "exams_lut_nov_2026.json"


def demo_plan():
    profile, exams = load(DEMO)
    needed = {e.name: estimator.estimate(e).hours for e in exams}
    return exams, scheduler.schedule(profile, exams, needed)


def test_every_agenda_fills_its_session_exactly():
    exams, plan = demo_plan()
    for s, steps in zip(plan.sessions, method.plan_agendas(plan, exams)):
        assert sum(step.minutes for step in steps) == round(s.hours * 60)
        assert all(step.minutes > 0 for step in steps)


def test_first_session_maps_the_course_and_new_topics_start_with_a_pretest():
    exams, plan = demo_plan()
    agendas = method.plan_agendas(plan, exams)
    types = method.session_types(plan, exams)
    for exam in exams:
        mine = sorted((i for i, s in enumerate(plan.sessions) if s.exam == exam.name),
                      key=lambda i: (plan.sessions[i].day, plan.sessions[i].start))
        assert agendas[mine[0]][0].key == "map"
        assert all(a.key != "map" for i in mine[1:] for a in agendas[i])
    for kind, steps in zip(types, agendas):
        keys = [s.key for s in steps]
        if kind == "new":
            assert "pretest" in keys and "overview" in keys
        if kind == "learn":
            assert keys[0] == "recall" and "pretest" not in keys


def test_a_topic_is_new_only_once():
    exam = Exam("Calc", 3, Location("LUT", "Lpr"), date=date(2026, 12, 1), topics=[Topic("A"), Topic("B")])
    sessions = [
        Session(date(2026, 11, d), time(9), 2, "Calc", "learn", topic)
        for d, topic in [(2, "A"), (3, "A"), (4, "A + B"), (5, "B")]
    ]
    plan = Plan(sessions, {"Calc": 8}, {"Calc": 8}, {})
    assert method.session_types(plan, [exam]) == ["new", "learn", "new", "learn"]


def test_mock_is_capped_at_the_exam_length_and_rest_is_marking():
    exam = Exam("Calc", 3, Location("LUT", "Lpr"), date=date(2026, 12, 1), duration_h=1.5)
    mock = Session(date(2026, 11, 20), time(9), 3, "Calc", "mock")
    steps = method.agenda(mock, "mock", exam)
    assert [(s.key, s.minutes) for s in steps] == [("mock", 90), ("mark", 90)]


def test_short_sessions_drop_the_smallest_steps():
    s = Session(date(2026, 11, 2), time(9), 0.25, "Calc", "learn")
    steps = method.agenda(s, "new", None)
    assert sum(x.minutes for x in steps) == 15 and len(steps) == 3


def test_category_changes_the_advice():
    assert method.how("practice", "math_proof") != method.how("practice", "memorization")
    assert method.how("recall", "math_proof") == method.HOW["recall"]


def test_calendar_description_lists_the_timed_steps():
    s = Session(date(2026, 11, 2), time(9), 2, "Calc", "practice", "Polar curves")
    text = method.describe(s, method.agenda(s, "practice", None), "math_computational")
    assert text.splitlines()[0] == "Polar curves"
    assert "09:00 Warm-up recall" in text and "sketch the region" in text
