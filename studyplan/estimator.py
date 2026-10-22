"""Estimate how many exam-preparation hours each exam needs."""

from __future__ import annotations

from dataclasses import dataclass

from .documents import DocEstimate
from .models import Exam

# Exam-prep hours per credit (ECTS) for a medium-difficulty course, starting from scratch.
HOURS_PER_CREDIT = {
    "math_proof": 9.0,
    "math_computational": 8.5,
    "statistics": 8.5,
    "programming": 7.5,
    "conceptual": 6.5,
    "memorization": 6.0,
}
DIFFICULTY_FACTOR = {1: 0.7, 2: 0.85, 3: 1.0, 4: 1.2, 5: 1.4}
TARGET_FACTOR = {"pass": 0.8, "good": 1.0, "top": 1.2}
DOCUMENT_WEIGHT = 0.6  # how much a document-based estimate counts vs. the credit-based one


@dataclass
class Estimate:
    exam: str
    hours: float
    source: str  # manual | credits | credits+documents
    detail: str


def estimate(exam: Exam, docs: DocEstimate | None = None) -> Estimate:
    if exam.hours is not None:
        return Estimate(exam.name, exam.hours, "manual", "hours set in the input file")

    knowledge = 1 - 0.6 * exam.prior_knowledge
    target = TARGET_FACTOR[exam.target]
    from_credits = (
        exam.credits
        * HOURS_PER_CREDIT[exam.category]
        * DIFFICULTY_FACTOR[exam.difficulty]
        * knowledge
        * target
    )
    detail = (
        f"{exam.credits:g} ECTS x {HOURS_PER_CREDIT[exam.category]:g} h ({exam.category}) "
        f"x difficulty {DIFFICULTY_FACTOR[exam.difficulty]:g} x knowledge {knowledge:.2f} "
        f"x target {target:g} = {from_credits:.1f} h"
    )
    if docs is None or docs.hours <= 0:
        return Estimate(exam.name, round(from_credits, 1), "credits", detail)

    # The documents measure the material itself, so difficulty is already reflected in them.
    from_docs = docs.hours * knowledge * target
    blended = (1 - DOCUMENT_WEIGHT) * from_credits + DOCUMENT_WEIGHT * from_docs
    detail += (
        f"; documents ({docs.summary()}) suggest {from_docs:.1f} h -> blended {blended:.1f} h"
    )
    return Estimate(exam.name, round(blended, 1), "credits+documents", detail)
