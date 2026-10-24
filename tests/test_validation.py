import json
from datetime import date

import pytest

from studyplan.models import Exam, InputError, Location, Profile, load

WHERE = Location("LUT", "Lappeenranta")
DAY = date(2026, 11, 30)


@pytest.mark.parametrize(
    "field, value, message",
    [
        ("difficulty", 7, "difficulty must be 1..5"),
        ("target", "excellent", "target must be one of"),
        ("prior_knowledge", 1.5, "prior_knowledge must be 0.0..1.0"),
        ("credits", 0, "credits must be positive"),
        ("mocks", -1, "mocks cannot be negative"),
        ("category", "cooking", "unknown category"),
    ],
)
def test_out_of_range_exam_values_are_rejected(field, value, message):
    kwargs = {"name": "Stats", "credits": 4, "location": WHERE, "date": DAY, field: value}
    with pytest.raises(InputError, match=message):
        Exam(**kwargs)


def test_zero_block_hours_is_rejected_instead_of_looping_forever():
    with pytest.raises(InputError, match="block_hours"):
        Profile("Lappeenranta", DAY, block_hours=0)


def _write(tmp_path, data) -> str:
    path = tmp_path / "in.json"
    path.write_text(json.dumps(data) if isinstance(data, dict) else data, encoding="utf-8")
    return str(path)


def test_missing_field_is_named(tmp_path):
    data = {"student": {"home_city": "Lappeenranta", "start_date": "2026-11-01"},
            "exams": [{"name": "Stats", "date": "2026-11-30", "university": "LUT", "city": "X"}]}
    with pytest.raises(InputError, match="'credits'"):
        load(_write(tmp_path, data))


def test_bad_date_weekday_and_json_are_reported(tmp_path):
    base = {"student": {"home_city": "L", "start_date": "2026-11-01"}, "exams": []}
    with pytest.raises(InputError, match="invalid date"):
        load(_write(tmp_path, {**base, "student": {"home_city": "L", "start_date": "1.11.2026"}}))
    with pytest.raises(InputError, match="invalid weekday"):
        load(_write(tmp_path, {**base, "student": {**base["student"], "rest_weekdays": ["sunday!", "xyz"]}}))
    with pytest.raises(InputError, match="not valid JSON"):
        load(_write(tmp_path, "{oops"))
