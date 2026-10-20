from studyplan.documents import classify, estimate_documents


def test_classify_statistics_text():
    text = "The random variable X has a normal distribution. Test the hypothesis using its variance."
    assert classify(text)[0] == "statistics"


def test_unknown_text_falls_back_to_conceptual():
    assert classify("hello world")[0] == "conceptual"


def test_estimate_counts_exercises_and_past_exams(tmp_path):
    sheet = tmp_path / "week1.txt"
    sheet.write_text(
        "Integral and derivative practice\nExercise 1 compute the integral\nExercise 2 find the derivative\n",
        encoding="utf-8",
    )
    past = tmp_path / "exam_2025.txt"
    past.write_text("Problem 1 integral", encoding="utf-8")

    result = estimate_documents([sheet, past])
    stats = {d.path: d for d in result.docs}
    assert result.category == "math_computational"
    assert stats[str(sheet)].exercises == 2
    assert stats[str(past)].is_past_exam
    # 1 page x 10 min + 2 exercises x 25 min = 1 h, plus one past exam (3 h)
    assert result.hours == 4.0
