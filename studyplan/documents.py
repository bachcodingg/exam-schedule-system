"""Read course documents (slides, exercise sheets, past exams) and estimate the workload.

Supported formats: .pdf (needs `pypdf`), .pptx (needs `python-pptx`), .txt and .md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .models import CATEGORIES

KEYWORDS = {
    "math_proof": ["theorem", "lemma", "proof", "corollary", "proposition", "q.e.d", "axiom"],
    "math_computational": [
        "integral", "derivative", "differentiat", "integrat", "limit", "series",
        "partial fraction", "chain rule", "taylor", "dx", "∫",
    ],
    "statistics": [
        "probability", "variance", "distribution", "hypothesis", "regression",
        "confidence interval", "estimator", "random variable", "expected value", "p-value",
    ],
    "programming": [
        "python", "matlab", "code", "algorithm", "simulation", "monte carlo",
        "def ", "import ", "function", "loop",
    ],
    "conceptual": [
        "protocol", "architecture", "agent", "network", "layer", "search",
        "knowledge", "routing", "concept", "model",
    ],
    "memorization": ["definition", "terminology", "history", "list of", "acronym"],
}
MINUTES_PER_PAGE = {
    "math_proof": 12, "math_computational": 10, "statistics": 9,
    "programming": 7, "conceptual": 5, "memorization": 6,
}
MINUTES_PER_EXERCISE = {
    "math_proof": 30, "math_computational": 25, "statistics": 20,
    "programming": 30, "conceptual": 12, "memorization": 8,
}
PAST_EXAM_HOURS = 3.0  # time to solve and review one past exam
MAX_PAST_EXAMS = 3
WORDS_PER_TEXT_PAGE = 400

EXERCISE_RE = re.compile(r"^\s*(exercise|problem|task|question|tehtävä)\s*\d", re.I | re.M)
FORMULA_RE = re.compile(r"[∫∑∏√≤≥≠≈∞∂λμσπ]|\\(frac|int|sum|sqrt)|\^\d|[a-z]_\{?\d")
PAST_EXAM_RE = re.compile(r"exam|tentti|midterm|final", re.I)


@dataclass
class DocStats:
    path: str
    pages: int
    words: int
    exercises: int
    formula_marks: int
    is_past_exam: bool


@dataclass
class DocEstimate:
    category: str
    hours: float
    scores: dict[str, int]
    docs: list[DocStats] = field(default_factory=list)


def extract_pages(path: str | Path) -> list[str]:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader

        return [page.extract_text() or "" for page in PdfReader(path).pages]
    if suffix == ".pptx":
        from pptx import Presentation

        return [
            "\n".join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame)
            for slide in Presentation(path).slides
        ]
    if suffix in (".txt", ".md"):
        words = path.read_text(encoding="utf-8").split(" ")
        return [
            " ".join(words[i : i + WORDS_PER_TEXT_PAGE])
            for i in range(0, max(len(words), 1), WORDS_PER_TEXT_PAGE)
        ]
    raise ValueError(f"Unsupported document type: {path.name}")


def classify(text: str) -> tuple[str, dict[str, int]]:
    """Pick the course category whose keywords appear most often."""
    lower = text.lower()
    scores = {cat: sum(lower.count(k) for k in KEYWORDS[cat]) for cat in CATEGORIES}
    best = max(scores, key=lambda c: scores[c])
    return (best if scores[best] > 0 else "conceptual"), scores


def analyse(path: str | Path) -> tuple[DocStats, str]:
    pages = extract_pages(path)
    text = "\n".join(pages)
    stats = DocStats(
        path=str(path),
        pages=len(pages),
        words=len(text.split()),
        exercises=len(EXERCISE_RE.findall(text)),
        formula_marks=len(FORMULA_RE.findall(text)),
        is_past_exam=bool(PAST_EXAM_RE.search(Path(path).stem)),
    )
    return stats, text


def estimate_documents(paths: list[str | Path], category: str | None = None) -> DocEstimate:
    """Estimate study hours from the material. `category` overrides the automatic guess."""
    analysed = [analyse(p) for p in paths]
    all_text = "\n".join(text for _, text in analysed)
    guessed, scores = classify(all_text)
    cat = category or guessed

    minutes = 0.0
    past_exams = 0
    for stats, _ in analysed:
        if stats.is_past_exam:
            past_exams += 1
            continue
        page_minutes = stats.pages * MINUTES_PER_PAGE[cat]
        if stats.pages and stats.formula_marks / stats.pages > 5:
            page_minutes *= 1.15  # formula-dense material reads slower
        minutes += page_minutes + stats.exercises * MINUTES_PER_EXERCISE[cat]
    hours = minutes / 60 + min(past_exams, MAX_PAST_EXAMS) * PAST_EXAM_HOURS

    return DocEstimate(cat, round(hours, 1), scores, [s for s, _ in analysed])
