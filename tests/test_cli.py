import json
from pathlib import Path

from studyplan.cli import expand_documents, main

EXAMPLE = Path(__file__).parent.parent / "data" / "exams_lut_2026.json"


def test_plan_writes_markdown_and_calendar(tmp_path):
    md, ics = tmp_path / "plan.md", tmp_path / "plan.ics"
    assert main(["plan", str(EXAMPLE), "--md", str(md), "--ics", str(ics)]) == 0
    assert md.read_text(encoding="utf-8").startswith("# Study plan")
    calendar = ics.read_bytes()
    assert calendar.startswith(b"BEGIN:VCALENDAR\r\n") and calendar.endswith(b"END:VCALENDAR\r\n")


def test_invalid_input_is_an_error_message_not_a_traceback(tmp_path, capsys):
    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    data["exams"][0]["difficulty"] = 9
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert main(["plan", str(path)]) == 2
    assert "difficulty must be 1..5" in capsys.readouterr().err


def test_missing_input_file_and_bad_hours(tmp_path, capsys):
    assert main(["plan", str(tmp_path / "nope.json")]) == 2
    assert main(["plan", str(EXAMPLE), "--hours", "30"]) == 2
    assert "--hours" in capsys.readouterr().err


def test_docs_accepts_folders_and_patterns(tmp_path, capsys, monkeypatch):
    (tmp_path / "calc").mkdir()
    (tmp_path / "calc" / "week1.txt").write_text("Exercise 1 integral\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert main(["docs", "calc"]) == 0
    folder = capsys.readouterr().out
    assert main(["docs", "calc/*.txt", "calc"]) == 0
    assert capsys.readouterr().out == folder  # matched twice, counted once
    assert main(["docs", "nothing/*.pdf"]) == 2


def test_absolute_glob_patterns(tmp_path):
    (tmp_path / "a.pdf").write_text("x", encoding="utf-8")
    found = expand_documents(Path("."), [str(tmp_path / "*.pdf")])
    assert [p.name for p in found] == ["a.pdf"]
