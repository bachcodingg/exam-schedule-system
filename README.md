# Exam Schedule System

An exam-aware study planner. You describe your exams (name, credits, date, time, university and
city, category) and, optionally, the course documents. The planner then:

1. **Estimates the workload** of every exam from its credits, category, difficulty, prior knowledge
   and target grade, and refines the estimate from your **documents** (slides, exercise sheets, past exams).
2. **Checks feasibility** before every deadline and tells you how far short you are, if at all.
3. **Builds a day-by-day plan** with a fixed number of study hours per day:
   - two focus blocks per day on *different* subjects (interleaving),
   - least-slack scheduling: the exam with the most work left per hour of time left goes first,
   - the day before each exam is review-only,
   - a mock exam at the real exam time a few days before each exam,
   - rest weekdays as buffer days, leftover time turned into extra practice.
4. **Checks exam-day logistics**: several exams in one slot (suggested time split), two exams on one
   day in different cities (travel time, conflicts), early exams away from home (stay overnight), and
   exams whose date is not confirmed yet.
5. **Exports** the plan as Markdown and as an `.ics` file for Google Calendar / Outlook / Apple Calendar.

## Quick start

```bash
pip install -r requirements.txt        # pypdf / python-pptx only needed for documents
python -m studyplan plan data/exams_lut_2026.json --md plan.md --ics plan.ics
```

Override the input file from the command line:

```bash
python -m studyplan plan data/exams_lut_2026.json --start 2026-10-25 --hours 3
```

Estimate the workload of a course from its documents:

```bash
python -m studyplan docs documents/stats2/*.pdf documents/stats2/exam_2025.pdf
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
      "documents": ["../documents/stats2/slides.pdf", "../documents/stats2/exam_2025.pdf"]
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
| `documents` | paths relative to the JSON file; `.pdf`, `.pptx`, `.txt`, `.md`. Files with *exam*, *tentti*, *midterm* or *final* in the name count as past exams |
| `assumed_date` | used while `date` is `null` (not announced yet) |
| `hours` | skip the estimate and use this number |

## How the workload is estimated

```
hours = credits x hours_per_credit[category] x difficulty x (1 - 0.6 x prior_knowledge) x target
```

With documents, the material is measured too (pages x minutes per page, exercises x minutes per
exercise, 3 h per past exam, slower for formula-dense pages). The final estimate is
40 % credit-based + 60 % document-based. All constants live at the top of `studyplan/estimator.py`
and `studyplan/documents.py`.

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
data/exams_lut_2026.json   example: six LUT exams in Nov-Dec 2026
tests/                      pytest suite
```

## Tests

```bash
python -m pytest
```

## Roadmap

- Adaptive rescheduling: mark sessions done/skipped and re-plan the rest
- Topic-level sessions from the document headings, with confidence ratings and spaced repetition
- LLM-based syllabus parsing and practice questions
- Web UI with a drag-and-drop calendar and a progress dashboard
- Post-exam retrospective that calibrates the estimates to you
