"""How to study: a timed agenda for every session, built on the best-supported learning techniques.

The method in one line: attempt first, learn new topics from worked examples, then practise
retrieval spaced over days and mixed across topics, rehearse the real exam, and log every
mistake until it is fixed. See PHASES, RULES and EVIDENCE for the reasoning.

Every session gets a recipe of steps with a share of its time:

- new      first session on a topic: pre-test, overview, worked examples, practice, recall
- learn    a topic seen before: warm-up recall, one harder example, practice, recall
- practice second round: mistakes-log recall, setup drill, mixed timed set, marking
- mock     full past exam under exam conditions, then marking
- review   formula sheet, mistakes log, one problem per topic, exam-day prep

The very first session of an exam also starts with a short map of the whole course.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .models import Exam, Plan, Session

STEP_ROUND = 5  # step lengths are rounded to this many minutes
MAP_SHARE = 0.15  # part of the first session of an exam spent mapping the course

RECIPES = {
    "new": [("recall", 0.05), ("pretest", 0.10), ("overview", 0.15), ("examples", 0.25),
            ("practice", 0.35), ("close", 0.10)],
    "learn": [("recall", 0.10), ("examples", 0.15), ("practice", 0.60), ("close", 0.15)],
    "practice": [("recall", 0.10), ("drill", 0.20), ("mixed", 0.55), ("mark", 0.15)],
    "mock": [("mock", 0.75), ("mark", 0.25)],
    "review": [("sheet", 0.20), ("mistakes", 0.30), ("one_each", 0.40), ("wrap", 0.10)],
    # The review day is split when it has several blocks for the same exam.
    "review_first": [("sheet", 0.40), ("mistakes", 0.60)],
    "review_last": [("one_each", 0.80), ("wrap", 0.20)],
}

STEP_NAME = {
    "map": "Map the course",
    "recall": "Warm-up recall",
    "pretest": "Pre-test",
    "overview": "Concept overview",
    "examples": "Worked examples",
    "practice": "Practice",
    "close": "Blank-page recall",
    "drill": "Setup drill",
    "mixed": "Mixed timed set",
    "mark": "Mark and log",
    "mock": "Mock exam",
    "sheet": "Formula sheet",
    "mistakes": "Mistakes log",
    "one_each": "One problem per topic",
    "wrap": "Exam-day prep",
}

HOW = {
    "map": "Skim the topic list and every overview, glance at one past exam to see the question "
           "types (do not solve it), and rate each topic 1-3. Your ratings steer the extra time.",
    "recall": "Without notes, redo two problems from earlier topics or from the mistakes log.",
    "pretest": "Attempt one problem on this topic cold, before reading anything. Getting it wrong "
               "is fine: trying first makes the explanation stick.",
    "overview": "Read the beginner overview once, then close it and write from memory: what "
                "problem this topic solves, the key formula or idea, and when to use it.",
    "examples": "Study the worked examples line by line and say why each step is allowed. Then "
                "cover the solution and redo the example yourself.",
    "practice": "Solve problems from easy to exam level. Attempt before looking; after 10 minutes "
                "stuck, uncover only the next line of the solution.",
    "close": "Blank page: write today's formulas and traps from memory, check, and copy what you "
             "missed to the formula sheet draft and the mistakes log.",
    "drill": "For 5-6 mixed problems only decide the method and write the setup, do not solve. "
             "Then check. Picking the method is what an exam tests and textbooks don't.",
    "mixed": "Problems from different topics in random order, timed at the exam's pace "
             "(minutes per point of the real exam).",
    "mark": "Mark against the solutions. Every lost point goes into the mistakes log with its "
            "cause: concept, setup, algebra or time.",
    "mock": "A full past exam under exam conditions: real start time, only the allowed aids, "
            "phone in another room, strictly timed.",
    "sheet": "Write the final formula sheet (or one-page summary) from memory first, then fill "
             "the gaps from your notes.",
    "mistakes": "Re-solve every mistakes-log entry from a blank page. Entries you get right twice "
                "are done.",
    "one_each": "One timed exam-level problem per topic, weakest topics first.",
    "wrap": "Pack for tomorrow (ID, allowed aids, route), set the time per question, stop early "
            "and sleep. No new material.",
}

# Category-specific versions of the steps where the subject changes how you practise.
HOW_BY_CATEGORY = {
    "math_computational": {
        "practice": "Solve from easy to exam level, writing every step. Check each answer: "
                    "differentiate the antiderivative, sanity-check sign and size. After 10 "
                    "minutes stuck, uncover only the next line.",
        "drill": "For 5-6 mixed problems only sketch the region and write the "
                 "integral with its limits, do not evaluate. Setup is where most points are lost.",
    },
    "math_proof": {
        "overview": "Read the overview, then write the key definitions word for word from memory. "
                    "Proofs fail on fuzzy definitions.",
        "examples": "For each proof write its skeleton (assumption, goal, key step) and why the key "
                    "step works. Then close it and rebuild the proof from the skeleton.",
        "practice": "Prove the statements yourself in full sentences. Stuck: unfold the "
                    "definitions, try a small case, or look for a counterexample.",
        "drill": "Strategy drill: for 5-6 mixed statements only decide true or false and the proof "
                 "idea (direct, contradiction, induction, counterexample).",
        "close": "From memory: definitions, theorem statements with all their conditions, and one "
                 "counterexample for each condition.",
    },
    "statistics": {
        "examples": "For each worked example name the model, the formula and what the result means "
                    "in one sentence. Then cover it and redo it.",
        "practice": "Solve by hand: write the model, derive, compute, and end with a one-sentence "
                    "interpretation. After 10 minutes stuck, uncover one line.",
        "drill": "Model drill: for 5-6 mixed problems only name the distribution or model and the "
                 "formula you would use. Then check.",
    },
    "programming": {
        "overview": "Read the overview, then write from memory: the idea, the core syntax or "
                    "algorithm, and when to use it.",
        "examples": "Trace the example code by hand on a small input, writing down the variable "
                    "values. Then close it and rewrite it from a blank file.",
        "practice": "Write code from a blank file, run it, test the edge cases. After 10 minutes "
                    "stuck, read one line of a solution and close it again.",
        "drill": "Trace drill: predict the output of 5-6 short snippets by hand, then run them.",
    },
    "conceptual": {
        "overview": "Read the overview, then explain the topic in plain words to an imaginary "
                    "beginner, on paper and without notes (Feynman technique).",
        "examples": "For each example ask why it works and how it differs from the neighbouring "
                    "concept. Fill a compare-and-contrast table.",
        "practice": "Answer exam-style questions in full sentences from memory, then compare with "
                    "the notes and fix the gaps.",
        "drill": "Explain drill: for 5-6 mixed terms write a two-sentence explanation and one "
                 "example each, then check.",
    },
    "memorization": {
        "overview": "Skim the material and turn it into question-and-answer flashcards, one fact "
                    "per card.",
        "examples": "Group the facts into stories, tables or mnemonics and link each one to "
                    "something you already know.",
        "practice": "Flashcards with active recall: answer before flipping. Wrong cards go back "
                    "into the pile until you get them right twice.",
        "drill": "Rapid recall: all cards of the earlier topics, shuffled.",
    },
}

PHASES = [
    ("1. Map", "first session",
     "Skim all overviews, look at one past exam, rate every topic 1-3.",
     "Shows where the hours have to go before you spend them."),
    ("2. Learn", "learn sessions, one topic after another",
     "Pre-test, overview, worked examples, practice, blank-page recall.",
     "Worked examples are the fastest way in for beginners; switch to solving alone as soon as you can."),
    ("3. Space and mix", "warm-up of every session, practice sessions",
     "Redo old problems, setup drills, mixed timed sets.",
     "Retrieval spread over days is the best-supported study technique; mixing teaches you to pick the method."),
    ("4. Rehearse", "mock exams",
     "A full past exam at the real time, then mark it.",
     "Practises what the exam really asks: choosing, pacing and writing under time pressure."),
    ("5. Consolidate", "review day",
     "Formula sheet, mistakes log, one problem per topic, sleep.",
     "No new material the day before; sleep consolidates what you learned."),
]

RULES = [
    "**Attempt before you look.** Reading a solution feels like understanding; only solving it "
    "proves you can.",
    "**10-minute stuck rule.** Then uncover one line of the solution, not the whole thing, and "
    "carry on yourself.",
    "**Two colours.** Everything you write after looking at help goes in a second colour, so you "
    "see honestly what you can do alone.",
    "**Close the book to check.** End every session with blank-page recall, not with rereading.",
    "**Keep a mistakes log.** Every lost point gets an entry: the problem, what went wrong, the "
    "fix, the cause (concept, setup, algebra, time). Re-solve entries after 1, 3 and 7 days.",
    "**Mix once you know the topics.** Before solving, write which method you will use and why.",
    "**Rate every topic 1-3** after each session and move spare time to the 1s.",
    "**Build the formula sheet as you go** (if one is allowed), from memory first. Writing it is "
    "a retrieval exercise, copying it is not.",
    "**Protect focus.** Phone in another room, 50 minutes of work, 5-10 minutes of break.",
    "**Sleep.** 7-9 hours, especially the two nights before the exam. No all-nighters.",
]

AVOID = (
    "Rereading, highlighting, copying out notes and watching solution videos feel productive but "
    "give an illusion of competence: you recognise the material without being able to produce it."
)

EVIDENCE = [
    "Practice testing and distributed practice are the two techniques rated *high utility* in the "
    "review by Dunlosky et al. (2013), *Psychological Science in the Public Interest*; rereading, "
    "highlighting and summarising are rated low.",
    "Retrieval beats restudying for long-term retention: Roediger & Karpicke (2006), "
    "*Psychological Science*.",
    "Spacing the same practice over days beats massing it: Cepeda et al. (2006), "
    "*Psychological Bulletin* (meta-analysis).",
    "Shuffled (interleaved) maths problems beat blocked ones on a delayed test, because students "
    "learn to pick the method: Rohrer & Taylor (2007), *Instructional Science*.",
    "Novices learn faster from worked examples than from solving alone (Sweller & Cooper, 1985); "
    "the advantage reverses as you gain expertise (Kalyuga et al., 2003, the expertise reversal "
    "effect), hence fewer examples and more practice in later sessions.",
    "Explaining each step to yourself improves learning from examples: Chi et al. (1989), "
    "*Cognitive Science*.",
    "Attempting a question before studying improves learning of the answer, even when the attempt "
    "fails: Richland, Kornell & Kao (2009), *Journal of Experimental Psychology: Applied*.",
    "Recalling until correct, then again in later sessions (successive relearning) gives durable "
    "memory: Rawson & Dunlosky (2011), *Journal of Experimental Psychology: General*.",
    "Sleep consolidates newly learned material: Diekelmann & Born (2010), "
    "*Nature Reviews Neuroscience*.",
]


@dataclass
class Step:
    key: str
    minutes: int

    @property
    def name(self) -> str:
        return STEP_NAME[self.key]


def how(key: str, category: str) -> str:
    return HOW_BY_CATEGORY.get(category, {}).get(key, HOW[key])


def _split(recipe: list[tuple[str, float]], minutes: int) -> list[Step]:
    """Share out the minutes, rounded to STEP_ROUND; the largest step absorbs the rounding.

    A session too short for every step keeps the steps with the largest shares.
    """
    recipe = list(recipe)
    while len(recipe) > 1 and len(recipe) * STEP_ROUND > minutes:
        recipe.remove(min(recipe, key=lambda r: r[1]))
    total = sum(share for _, share in recipe)
    steps = [Step(key, max(STEP_ROUND, round(minutes * share / total / STEP_ROUND) * STEP_ROUND))
             for key, share in recipe]
    biggest = max(steps, key=lambda s: s.minutes)
    biggest.minutes += minutes - sum(s.minutes for s in steps)
    return steps


def _mock_steps(minutes: int, exam: Exam | None) -> list[Step]:
    attempt = minutes - max(STEP_ROUND, round(minutes * 0.25 / STEP_ROUND) * STEP_ROUND)
    if exam:
        attempt = min(attempt, round(exam.duration_h * 60))
    return [Step("mock", attempt), Step("mark", minutes - attempt)]


def _by_time(plan: Plan) -> list[int]:
    return sorted(range(len(plan.sessions)), key=lambda i: (plan.sessions[i].day, plan.sessions[i].start))


def session_types(plan: Plan, exams: list[Exam]) -> list[str]:
    """The RECIPES key of every session in plan.sessions.

    A learn session is "new" when it reaches a topic not seen before (or the exam has no
    topics, so every session moves on through the material), otherwise "learn".
    """
    has_topics = {e.name: bool(e.topics) for e in exams}
    seen: dict[str, set[str]] = {}
    reviews: dict[tuple, list[int]] = {}
    types = [""] * len(plan.sessions)
    for i in _by_time(plan):
        s = plan.sessions[i]
        if s.kind == "learn":
            topics = set(s.topic.split(" + ")) if s.topic else set()
            known = seen.get(s.exam)
            new = known is None or not has_topics.get(s.exam) or bool(topics - known)
            seen.setdefault(s.exam, set()).update(topics)
            types[i] = "new" if new else "learn"
        else:
            types[i] = s.kind
            if s.kind == "review":
                reviews.setdefault((s.day, s.exam), []).append(i)
    for same_day in reviews.values():
        if len(same_day) > 1:
            for i in same_day:
                types[i] = "review_first" if i != same_day[-1] else "review_last"
    return types


def agenda(session: Session, kind: str, exam: Exam | None, first_of_exam: bool = False) -> list[Step]:
    """Timed steps for one session. `kind` is a RECIPES key from session_types()."""
    minutes = round(session.hours * 60)
    if kind == "mock":
        return _mock_steps(minutes, exam)
    recipe = RECIPES[kind]
    if first_of_exam:
        # Nothing to recall yet: map the course instead.
        recipe = [("map", MAP_SHARE)] + [(k, share) for k, share in recipe if k != "recall"]
    return _split(recipe, minutes)


def plan_agendas(plan: Plan, exams: list[Exam]) -> list[list[Step]]:
    """An agenda for every session, in the order of plan.sessions."""
    by_name = {e.name: e for e in exams}
    types = session_types(plan, exams)
    started: set[str] = set()
    agendas: list[list[Step]] = [[] for _ in plan.sessions]
    for i in _by_time(plan):
        s = plan.sessions[i]
        studying = types[i] in ("new", "learn", "practice")
        agendas[i] = agenda(s, types[i], by_name.get(s.exam), first_of_exam=studying and s.exam not in started)
        if studying:
            started.add(s.exam)
    return agendas


def timed(session: Session, steps: list[Step]) -> list[tuple[str, Step]]:
    """(start "HH:MM", step) pairs."""
    clock = datetime.combine(session.day, session.start)
    out = []
    for step in steps:
        out.append((f"{clock:%H:%M}", step))
        clock += timedelta(minutes=step.minutes)
    return out


def describe(session: Session, steps: list[Step], category: str) -> str:
    """Plain-text agenda, e.g. for a calendar event description."""
    lines = [session.topic or ""] if session.topic else []
    for start, step in timed(session, steps):
        lines.append(f"{start} {step.name} ({step.minutes} min): {how(step.key, category)}")
    return "\n".join(lines)
