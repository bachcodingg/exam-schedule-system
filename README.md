# Exam Schedule System

An exam-aware study planner. You describe your exams (name, credits, date, time, university and
city, category) and, optionally, the course documents. The planner then:

1. **Estimates the workload** of every exam from its credits, category, difficulty, prior knowledge
   and target grade, and refines the estimate from your **documents** (slides, exercise sheets, past exams).
   Past exams are recognised by their exam header, not only by file name.
2. **Checks feasibility** before every deadline and tells you how far short you are, if at all.
3. **Builds a day-by-day plan** with a fixed number of study hours per day:
   - two focus blocks per day on *different* subjects (interleaving),
   - least-slack scheduling: the exam with the most work left per hour of time left goes first,
   - learn sessions walk through the exam's **topics** in order, sized by weight (e.g. exam points),
   - the last free day before each exam is review-only (moved earlier for back-to-back exam days),
   - one or more spaced mock exams at the real exam time before each exam,
   - rest weekdays as buffer days, leftover time turned into a second, spaced round over the topics.
4. **Checks exam-day logistics**: several exams in one slot (suggested time split), two exams on one
   day in different cities (travel time, conflicts), early exams away from home (stay overnight), and
   exams whose date or start time is not confirmed yet.
5. **Exports** the plan as Markdown and as an `.ics` file for Google Calendar / Outlook / Apple Calendar.

## Demo

[`docs/demo/plan_nov_2026.md`](docs/demo/plan_nov_2026.md) is a real plan for three LUT exams
(Integral Calculus and Statistics II on 30.11, Matrix Algebra on 1.12), generated from
[`data/exams_lut_nov_2026.json`](data/exams_lut_nov_2026.json) plus 30 course files (past exams,
exercise sheets with solutions, lecture summary, cheat sheets). Import
[`docs/demo/plan_nov_2026.ics`](docs/demo/plan_nov_2026.ics) into a calendar to see it there.
The course files themselves are not in the repo, so re-running the demo without them gives a
credit-based estimate only.

What the document analysis found:

| Course | Files | Detected | Estimate |
|---|---|---|---|
| Integral Calculus | 3 past exams, cheat sheet (.docx), photo | `math_computational`, 3 past exams, no course material | 21 h |
| Statistics II | 2 past exams, lecture summary, 6 solution sets | `statistics`, 2 past exams, 14 exercises | 19 h |
| Matrix Algebra | 1 past exam, Q&A, 7 exercise sets + solutions, formula sheet | `math_proof`, 113 exercises | 38 h |

## Quick start

```bash
pip install -r requirements.txt        # pypdf / python-pptx only needed for documents
python -m studyplan plan data/exams_lut_2026.json --md plan.md --ics plan.ics
python -m studyplan plan data/exams_lut_nov_2026.json --md plan.md   # the demo, with topics
```

Override the input file from the command line:

```bash
python -m studyplan plan data/exams_lut_2026.json --start 2026-10-25 --hours 3
```

Estimate the workload of a course from its documents:

```bash
python -m studyplan docs documents/stats2/*
```

## Input file

```json
{
  "student": {
    "home_city": "Lappeenranta",
    "start_date": "2026-10-21",
    "daily_hours": 4,
    "block_hours": 2,
    "rest_weekdays": ["sun"],
    "blocked_dates": ["2026-11-14"]
  },
  "exams": [
    {
      "name": "Statistics II", "credits": 4, "category": "statistics",
      "date": "2026-11-30", "start": "16:30", "duration_h": 3,
      "university": "LUT", "city": "Lappeenranta",
      "difficulty": 3, "prior_knowledge": 0.2, "target": "good",
      "documents": ["../documents/stats2"],
      "mocks": 2,
      "topics": [
        {"name": "Priors and conjugacy", "weight": 10},
        {"name": "MLE", "weight": 10},
        "Time series"
      ]
    },
    {
      "name": "Advanced Computer Networks", "credits": 3, "category": "conceptual",
      "date": null, "assumed_date": "2026-12-18",
      "university": "LUT", "city": "Lahti"
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `category` | `math_proof`, `math_computational`, `statistics`, `programming`, `conceptual`, `memorization` |
| `difficulty` | 1 (easy) to 5 (very hard), default 3 |
| `prior_knowledge` | 0.0 to 1.0, how much you already know |
| `target` | `pass`, `good` or `top` |
| `documents` | files, folders or glob patterns relative to the JSON file; `.pdf`, `.pptx`, `.docx`, `.txt`, `.md` (other files are skipped with a note). See below for how files are classified |
| `topics` | study order; each a name or `{"name", "weight"}`. Weight = share of the time, e.g. typical exam points |
| `mocks` | number of timed mock exams, default 1. One per past exam you have is a good choice |
| `assumed_date` | used while `date` is `null` (not announced yet) |
| `hours` | skip the estimate and use this number |

## How the workload is estimated

```
hours = credits x hours_per_credit[category] x difficulty x (1 - 0.6 x prior_knowledge) x target
```

With documents, the material is measured too (pages x minutes per page, exercises x minutes per
exercise, 3 h per past exam, slower for formula-dense pages). The final estimate is
40 % credit-based + 60 % document-based. If the documents are only past exams and cheat sheets,
they measure the practice but not the learning, so they can raise the estimate but never lower it.
All constants live at the top of `studyplan/estimator.py` and `studyplan/documents.py`.

Each file gets a kind:

| Kind | Recognised by | Counts as |
|---|---|---|
| past exam | *exam*, *tentti*, *midterm*, *final* in the name, or an exam header on page 1 (`Exam 7.10.2025`, `Allowed tools`, `Answer all questions`) | 3 h each, at most 3 |
| reference | *sheet*, *cheat*, *formula*, *summary*, *plan*, *notes* in the name | reading time only |
| solutions | *solution*, *ratkaisu* in the name | half the exercise time |
| material | everything else | pages + exercises |

Exercises are distinct task numbers (`Exercise 3`, `Problem 2`, or a line starting `4. Let ...`),
so a bilingual exam is not counted twice.

## Project layout

```
studyplan/
  models.py       Exam, Profile, Session, Plan + JSON loader
  estimator.py    workload estimate per exam
  documents.py    text extraction, category detection, document-based hours
  timeline.py     study / review / exam / buffer days
  feasibility.py  needed vs. available hours before each deadline
  scheduler.py    least-slack scheduler with interleaving, mocks and review days
  logistics.py    shared slots, travel between cities, early exams
  export.py       Markdown and .ics output
  cli.py          `plan` and `docs` commands
data/exams_lut_2026.json      example: six LUT exams in Nov-Dec 2026
data/exams_lut_nov_2026.json  demo: three exams with topics, mocks and documents
docs/demo/                    the generated demo plan (.md and .ics)
tests/                      pytest suite
```

## Tests

```bash
python -m pytest
```

## Roadmap

- Adaptive rescheduling: mark sessions done/skipped and re-plan the rest
- Topics read from the document headings, with confidence ratings that reweight them
- LLM-based syllabus parsing and practice questions
- Web UI with a drag-and-drop calendar and a progress dashboard
- Post-exam retrospective that calibrates the estimates to you
