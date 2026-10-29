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


DEMO = Path(__file__).parent.parent / "data" / "exams_lut_nov_2026.json"


def test_guide_writes_one_file_per_exam_with_content(tmp_path, capsys):
    assert main(["guide", str(DEMO), "--out", str(tmp_path)]) == 0
    names = sorted(p.name for p in tmp_path.iterdir())
    assert names == ["guide_integral_calculus.md", "guide_matrix_algebra.md", "guide_statistics_ii.md"]
    calc = (tmp_path / "guide_integral_calculus.md").read_text(encoding="utf-8")
    for heading in ("## 1. Workload", "## 2. How to study", "## 3. Session by session",
                    "## 5. Practice exam", "## Appendix B: Practice exam answer key"):
        assert heading in calc
    assert "#### Worked examples" in calc and "Paper: the practice exam in section 5." in calc
    stats = (tmp_path / "guide_statistics_ii.md").read_text(encoding="utf-8")
    assert "Write your own beginner overview" in stats and "## 5. Practice exam" not in stats
    assert "study days" in capsys.readouterr().out


def test_guide_for_one_exam_and_own_pack(tmp_path):
    data = json.loads(DEMO.read_text(encoding="utf-8"))
    for exam in data["exams"]:
        exam["documents"] = []
    data["exams"][1]["pack"] = "stats.md"
    (tmp_path / "stats.md").write_text(
        "---\ncourse: My Stats\n---\n# Topic: Priors\nkeywords: prior\n## Overview\nBayes.\n", encoding="utf-8"
    )
    path = tmp_path / "in.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    out = tmp_path / "out"
    assert main(["guide", str(path), "--out", str(out), "--exam", "statistics ii"]) == 0
    assert [p.name for p in out.iterdir()] == ["guide_statistics_ii.md"]
    assert "Bayes." in (out / "guide_statistics_ii.md").read_text(encoding="utf-8")
    assert main(["guide", str(path), "--out", str(out), "--exam", "Nope"]) == 2


def test_plan_has_workload_and_calendar_agendas(tmp_path):
    md, ics = tmp_path / "plan.md", tmp_path / "plan.ics"
    assert main(["plan", str(EXAMPLE), "--md", str(md), "--ics", str(ics)]) == 0
    assert "## Workload" in md.read_text(encoding="utf-8")
    unfolded = ics.read_text(encoding="utf-8").replace("\r\n ", "")
    assert "Map the course" in unfolded
