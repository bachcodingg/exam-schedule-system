from datetime import date, time

from studyplan.export import _fold, to_ics
from studyplan.models import Exam, Location, Plan, Session

DAY = date(2026, 11, 30)


def _plan(sessions):
    return Plan(sessions, {}, {}, {})


def test_special_characters_are_escaped():
    exam = Exam("Signals, Systems; II", 5, Location("TUM", "Munich"), date=DAY, start=time(9, 0))
    ics = to_ics(_plan([]), [exam], "Europe/Berlin")
    assert "SUMMARY:EXAM: Signals\\, Systems\\; II" in ics
    assert "DTSTART;TZID=Europe/Berlin:20261130T090000" in ics


def test_long_lines_are_folded_to_75_octets():
    topic = "Solids of revolution: disk/washer/shell, surface area, mass, " * 4
    ics = to_ics(_plan([Session(date(2026, 11, 2), time(9, 0), 2, "Calculus", "learn", topic)]), [])
    lines = ics.split("\r\n")
    assert all(len(line.encode("utf-8")) <= 75 for line in lines)
    assert any(line.startswith(" ") for line in lines)


def test_fold_never_splits_a_multibyte_character():
    line = "DESCRIPTION:" + "ä" * 100
    parts = _fold(line)
    assert "".join(p.lstrip(" ") if i else p for i, p in enumerate(parts)) == line
    assert all(len(p.encode("utf-8")) <= 75 for p in parts)


def test_assumed_exam_date_is_marked():
    exam = Exam("Nets", 3, Location("LUT", "Lahti"), assumed_date=DAY, start=time(9, 0))
    assert "SUMMARY:EXAM (date not confirmed): Nets" in to_ics(_plan([]), [exam])
