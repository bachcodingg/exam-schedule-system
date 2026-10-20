from datetime import date

from studyplan.documents import DocEstimate
from studyplan.estimator import estimate
from studyplan.models import Exam, Location

LUT = Location("LUT", "Lappeenranta")


def make(**kwargs) -> Exam:
    defaults = dict(name="X", credits=5, location=LUT, date=date(2026, 12, 1), category="statistics")
    return Exam(**{**defaults, **kwargs})


def test_credit_based_estimate():
    assert estimate(make()).hours == 42.5


def test_harder_exam_needs_more_time():
    assert estimate(make(difficulty=5)).hours > estimate(make(difficulty=3)).hours


def test_prior_knowledge_reduces_time():
    assert estimate(make(prior_knowledge=0.5)).hours < estimate(make()).hours


def test_manual_hours_win():
    result = estimate(make(hours=10))
    assert result.hours == 10 and result.source == "manual"


def test_documents_are_blended_in():
    docs = DocEstimate("statistics", hours=100, scores={})
    result = estimate(make(), docs)
    assert result.source == "credits+documents"
    assert 42.5 < result.hours < 100
