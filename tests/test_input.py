import json

from studyplan.cli import expand_documents
from studyplan.models import load


def test_documents_accept_folders_and_globs(tmp_path):
    (tmp_path / "stats").mkdir()
    for name in ("a.pdf", "b.pdf", "c.txt"):
        (tmp_path / "stats" / name).write_text("x", encoding="utf-8")
    assert [p.name for p in expand_documents(tmp_path, ["stats"])] == ["a.pdf", "b.pdf", "c.txt"]
    assert [p.name for p in expand_documents(tmp_path, ["stats/*.pdf"])] == ["a.pdf", "b.pdf"]
    assert [p.name for p in expand_documents(tmp_path, ["stats/c.txt"])] == ["c.txt"]


def test_topics_and_mocks_are_loaded(tmp_path):
    data = {
        "student": {"home_city": "Lappeenranta", "start_date": "2026-11-01"},
        "exams": [{
            "name": "Stats", "credits": 4, "date": "2026-11-30", "university": "LUT",
            "city": "Lappeenranta", "mocks": 2,
            "topics": ["Priors", {"name": "MCMC", "weight": 3}],
        }],
    }
    path = tmp_path / "in.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    exam = load(path)[1][0]
    assert exam.mocks == 2
    assert [(t.name, t.weight) for t in exam.topics] == [("Priors", 1.0), ("MCMC", 3)]
