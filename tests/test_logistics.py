from datetime import date, time

from studyplan.logistics import check
from studyplan.models import Exam, Location, Profile

HOME = Profile(home_city="Lappeenranta", start_date=date(2026, 12, 1))
DAY = date(2026, 12, 22)


def test_double_exam_day_across_cities_is_flagged():
    ai = Exam("AI", 6, Location("LUT", "Lahti"), date=DAY, start=time(8, 0))
    sim = Exam("Sim", 5, Location("LUT", "Lappeenranta"), date=DAY, start=time(16, 30))
    notes = check(HOME, [ai, sim])
    assert any("double exam day" in n for n in notes)
    assert any("stay overnight" in n for n in notes)


def test_impossible_travel_is_a_conflict():
    a = Exam("A", 3, Location("LUT", "Lahti"), date=DAY, start=time(9, 0), duration_h=3)
    b = Exam("B", 3, Location("LUT", "Lappeenranta"), date=DAY, start=time(13, 0))
    assert any(n.startswith("CONFLICT") for n in check(HOME, [a, b]))


def test_shared_slot_suggests_time_split():
    a = Exam("A", 3, Location("LUT", "Lappeenranta"), date=DAY, start=time(16, 30))
    b = Exam("B", 4, Location("LUT", "Lappeenranta"), date=DAY, start=time(16, 30))
    assert any("share one slot" in n for n in check(HOME, [a, b]))


def test_unconfirmed_date_is_mentioned():
    a = Exam("Nets", 3, Location("LUT", "Lahti"), assumed_date=DAY)
    assert any("not confirmed" in n for n in check(HOME, [a]))


def test_city_names_match_regardless_of_case():
    a = Exam("A", 3, Location("LUT", "lahti"), date=DAY, start=time(9, 0), duration_h=3)
    b = Exam("B", 3, Location("LUT", "LAPPEENRANTA "), date=DAY, start=time(13, 0))
    notes = check(HOME, [a, b])
    assert any(n.startswith("CONFLICT") for n in notes)
    assert not any("travel time unknown" in n for n in notes)
