# Exam Schedule System

[![tests](https://github.com/bachcodingg/exam-schedule-system/actions/workflows/tests.yml/badge.svg)](https://github.com/bachcodingg/exam-schedule-system/actions/workflows/tests.yml)

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
5. **Turns the hours into days**: 50 h at 3 h/day is 17 study days; next to that it shows the study
   days the calendar really has and the latest start date that still fits every estimate.
6. **Writes a study guide per exam**: a timed agenda for every session (what to do, minute by
   minute, and why), the study method, and the course content: beginner overviews, worked
   examples, common mistakes, practice problems, a full practice exam and the answer keys.
7. **Exports** the plan as Markdown and as an `.ics` file for Google Calendar / Outlook / Apple
   Calendar. Every calendar event carries its session agenda.

## Demo

[`docs/demo/plan_nov_2026.md`](docs/demo/plan_nov_2026.md) is a real plan for three LUT exams
(Integral Calculus and Statistics II on 30.11, Matrix Algebra on 1.12), generated from
[`data/exams_lut_nov_2026.json`](data/exams_lut_nov_2026.json) plus 30 course files (past exams,
exercise sheets with solutions, lecture summary, cheat sheets). Import
[`docs/demo/plan_nov_2026.ics`](docs/demo/plan_nov_2026.ics) into a calendar to see it there.
[`docs/demo/guide_integral_calculus.md`](docs/demo/guide_integral_calculus.md) is the study guide
for the first exam, with the built-in Integral Calculus content.
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
python -m studyplan guide data/exams_lut_nov_2026.json --out guides  # one study guide per exam
python -m studyplan guide data/exams_lut_nov_2026.json --exam "Integral Calculus"
```

Override the input file from the command line:

```bash
python -m studyplan plan data/exams_lut_2026.json --start 2026-10-25 --hours 3
```

Estimate the workload of a course from its documents (files, folders or quoted glob patterns,
so it works the same in PowerShell and bash):

```bash
python -m studyplan docs documents/stats2
python -m studyplan docs "documents/calc/*.pdf"
```

Invalid input is reported as `error: ...` with exit code 2, naming the exam and the field,
e.g. `error: Statistics II: difficulty must be 1..5, got 7`. Corrupt or encrypted documents
are skipped and listed under the warnings instead of stopping the plan.

## Input file

```json
{
  "student": {
    "home_city": "Lappeenranta",
    "start_date": "2026-10-21",
    "daily_hours": 4,
    "block_hours": 2,
    "rest_weekdays": ["sun"],
    "blocked_dates": ["2026-11-14"],
    "timezone": "Europe/Helsinki"
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
| `pack` | content pack (`.md`) for the study guide, relative to the JSON file. Without it a built-in pack is used when its name matches the exam |
| `timezone` (student) | IANA name for the `.ics` times, default `Europe/Helsinki` |

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

## Study guides and the study method

`python -m studyplan guide input.json` writes `guides/guide_<exam>.md` for every exam:

1. **Workload**: the estimate in study days at your daily hours, the days the calendar has, what
   the plan gives the exam (learning, practice, mocks, review) and the new material per week.
2. **How to study**: the method below, its rules and the research behind it.
3. **Session by session**: every session with its timed steps, e.g.
   `09:00 Warm-up recall 10′ → 09:10 Worked examples 20′ → 09:30 Practice 70′ → 10:40 Blank-page recall 20′`,
   and for each mock exam the paper to sit (the pack's practice exam first, your real past exams last).
4. **Topics**: per topic a beginner overview, worked examples, common mistakes and practice problems.
5. **Practice exam**, then the appendix: answers (kept apart so every attempt is real), the
   practice exam answer key, a mistakes log and a topic confidence tracker.

The method in one line: *attempt first, learn new topics from worked examples, then practise
retrieval spaced over days and mixed across topics, rehearse the real exam, and log every mistake
until it is fixed.* Each session type has its own recipe (`studyplan/method.py`):

| Session | Steps (share of the time) |
|---|---|
| new topic | warm-up recall 5 %, pre-test 10 %, concept overview 15 %, worked examples 25 %, practice 35 %, blank-page recall 10 % |
| learn (topic seen before) | warm-up recall 10 %, worked examples 15 %, practice 60 %, blank-page recall 15 % |
| practice (second round) | mistakes-log recall 10 %, setup drill 20 %, mixed timed set 55 %, mark and log 15 % |
| mock | the past exam under exam conditions (at most the exam's length), the rest marking |
| review day | formula sheet, mistakes log, one timed problem per topic, exam-day prep |

The first session of every exam starts by mapping the course instead of recalling. How a step is
done depends on the category: a setup drill means *sketch the region and write the integral* in
`math_computational`, *decide true/false and the proof idea* in `math_proof`, *name the model* in
`statistics`. The choices follow the learning research: retrieval practice and spacing (rated
the two most useful techniques by Dunlosky et al., 2013), interleaving for picking the method
(Rohrer & Taylor, 2007), worked examples for beginners, fading as you improve (Sweller & Cooper,
1985; Kalyuga et al., 2003), self-explanation (Chi et al., 1989) and pretesting (Richland et al., 2009).

### Content packs

A pack is a Markdown file with one `# Topic:` section per topic (`## Overview`, `## Worked
examples`, `## Common mistakes`, `## Practice`, `## Answers`), plus `# Practice exam` and
`# Practice exam answers`. Formulas are written as `$...$` (rendered by GitHub and VS Code).
Exam topics are matched to pack topics by the `keywords:` line under each topic heading.
[`studyplan/packs/integral_calculus.md`](studyplan/packs/integral_calculus.md) is built in and is
used automatically for an exam named *Integral Calculus* (or *BM20A8100*). For other courses the
guide still has the method and the agendas, lists your documents as the sources, and gives a
template for writing each overview yourself. To get the full content, write a pack in the same
format, or ask Claude to write one from your course files, and set `"pack": "packs/stats2.md"`.

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
  workload.py     hours -> study days, latest start date
  method.py       the study method: a timed agenda for every session
  packs.py        content packs (overviews, examples, practice exams)
  packs/          built-in packs: integral_calculus.md
  guide.py        the study guide per exam
  export.py       Markdown and .ics output
  cli.py          `plan`, `guide` and `docs` commands
data/exams_lut_2026.json      example: six LUT exams in Nov-Dec 2026
data/exams_lut_nov_2026.json  demo: three exams with topics, mocks and documents
docs/demo/                    the generated demo plan (.md and .ics) and study guide
tests/                      pytest suite
```

## Tests

```bash
python -m pytest
```

## Known limitations

- The constants (hours per credit, minutes per page, ...) are hand-tuned on a few LUT courses,
  not calibrated on data. Treat the estimate as a starting point and use `hours` to override it.
- `TRAVEL_HOURS` in `studyplan/logistics.py` only knows Lappeenranta, Lahti and Helsinki; other
  city pairs are reported as "travel time unknown" until you add them.
- The plan is static: it does not know which sessions you actually did. Re-run it with a new
  `--start` date after falling behind.
- The `.ics` file names its time zone (`TZID`) without a `VTIMEZONE` block. Google, Outlook
  and Apple Calendar resolve IANA names themselves; strict validators may complain.

## Roadmap

- Adaptive rescheduling: mark sessions done/skipped and re-plan the rest
- Topics read from the document headings, with confidence ratings that reweight them
- More built-in packs (Statistics II, Matrix Algebra), and packs generated from the course files
- Web UI with a drag-and-drop calendar and a progress dashboard
- Post-exam retrospective that calibrates the estimates to you
