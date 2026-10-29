from studyplan import packs

PACK = """---
course: Toy Course
match: toy course, tc101
---

# Topic: Solids of revolution
keywords: solid, revolution, washer

## Overview

Spin it.

## Worked examples

### Example 1

Disk.

## Answers

1. $8\\pi$

# Topic: Parametric curves
keywords: parametric

## Overview

Move along t.

# Practice exam

**1.** Question.

# Practice exam answers

**1.** Answer.
"""


def test_parse_sections_and_exam():
    pack = packs.parse(PACK)
    assert pack.course == "Toy Course" and pack.match == ["toy course", "tc101"]
    assert [t.title for t in pack.topics] == ["Solids of revolution", "Parametric curves"]
    solids = pack.topics[0]
    assert solids.keywords == ["solid", "revolution", "washer"]
    assert solids.sections["overview"] == "Spin it."
    assert "### Example 1" in solids.sections["worked examples"]
    assert pack.exam == "**1.** Question." and pack.exam_answers == "**1.** Answer."


def test_topic_matching_prefers_the_part_before_the_colon():
    pack = packs.parse(PACK)
    assert pack.topic_for("Parametric curves: area, arc length, surface of revolution").title == "Parametric curves"
    assert pack.topic_for("Solids of revolution: disk/washer/shell").title == "Solids of revolution"
    assert pack.topic_for("Time series") is None


def test_builtin_integral_calculus_pack_covers_the_demo_topics():
    pack = packs.find("Integral Calculus")
    assert pack is not None and pack.exam and pack.exam_answers
    for topic in pack.topics:
        assert {"overview", "worked examples", "practice", "answers"} <= set(topic.sections), topic.title
    assert packs.find("Statistics II") is None


def test_demote_shifts_headings_only():
    assert packs.demote("## A\ntext # not a heading\n### B", 1) == "### A\ntext # not a heading\n#### B"
