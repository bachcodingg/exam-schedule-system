"""Content packs: beginner overviews, worked examples, practice problems and a practice exam.

A pack is a Markdown file:

    ---
    course: Integral Calculus
    match: integral calculus, integraalilaskenta, bm20a8100
    ---
    # Topic: Solids of revolution
    keywords: solid, revolution, washer, shell
    ## Overview
    ## Worked examples
    ## Common mistakes
    ## Practice
    ## Answers
    # Practice exam
    # Practice exam answers

An exam uses the pack named by its `pack` field, or else a built-in pack whose `match`
terms appear in the exam name. Exam topics are matched to pack topics by keywords.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

BUILTIN = Path(__file__).parent / "packs"
SECTIONS = ("overview", "worked examples", "common mistakes", "practice", "answers")
HEAD_WEIGHT = 3  # a keyword in the part of a topic name before ":" counts this much more


@dataclass
class PackTopic:
    title: str
    keywords: list[str]
    sections: dict[str, str] = field(default_factory=dict)  # SECTIONS -> Markdown


@dataclass
class Pack:
    course: str
    match: list[str]
    topics: list[PackTopic]
    exam: str = ""  # practice exam questions
    exam_answers: str = ""
    path: str = ""

    def topic_for(self, name: str) -> PackTopic | None:
        """The pack topic whose keywords best match an exam topic name."""
        head, _, rest = name.lower().partition(":")
        scored = [
            (sum(HEAD_WEIGHT * (k in head) + (k in rest) for k in t.keywords), -i, t)
            for i, t in enumerate(self.topics)
        ]
        score, _, best = max(scored, key=lambda x: x[:2], default=(0, 0, None))
        return best if score > 0 else None


def _split(text: str, level: int) -> list[tuple[str, str]]:
    """[(heading, body)] for headings of exactly `level` hashes; text before the first is ''."""
    parts = re.split(rf"^{'#' * level} (?!#)(.*)$", text, flags=re.M)
    out = [("", parts[0])]
    out += [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]
    return out


def parse(text: str, path: str = "") -> Pack:
    meta = {}
    front = re.match(r"\A---\n(.*?)\n---\n", text.replace("\r\n", "\n"), re.S)
    body = text.replace("\r\n", "\n")
    if front:
        for line in front.group(1).splitlines():
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip()
        body = body[front.end():]
    pack = Pack(
        course=meta.get("course", Path(path).stem),
        match=[m.strip().lower() for m in meta.get("match", "").split(",") if m.strip()],
        topics=[],
        path=path,
    )
    for heading, chunk in _split(body, 1)[1:]:
        lower = heading.lower()
        if lower.startswith("topic:"):
            keywords = re.search(r"^keywords:(.*)$", chunk, re.M)
            topic = PackTopic(
                heading.split(":", 1)[1].strip(),
                [k.strip().lower() for k in keywords.group(1).split(",")] if keywords else [],
            )
            for name, section in _split(chunk, 2)[1:]:
                topic.sections[name.lower()] = section.strip()
            pack.topics.append(topic)
        elif lower == "practice exam":
            pack.exam = chunk.strip()
        elif lower in ("practice exam answers", "practice exam answer key"):
            pack.exam_answers = chunk.strip()
    return pack


def load(path: str | Path) -> Pack:
    return parse(Path(path).read_text(encoding="utf-8"), str(path))


def find(exam_name: str, directory: Path = BUILTIN) -> Pack | None:
    """A built-in pack whose match terms appear in the exam name."""
    name = exam_name.lower()
    for path in sorted(directory.glob("*.md")):
        pack = load(path)
        if any(term in name for term in pack.match):
            return pack
    return None


def demote(markdown: str, levels: int) -> str:
    """Push every heading `levels` deeper, so a pack section fits under a guide heading."""
    return re.sub(r"^(#+) ", lambda m: "#" * min(len(m.group(1)) + levels, 6) + " ", markdown, flags=re.M)
