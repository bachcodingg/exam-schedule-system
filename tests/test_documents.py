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


def test_past_exam_recognised_by_header_not_file_name(tmp_path):
    past = tmp_path / "BM20A8100_Integraalilaskenta_07102025.txt"
    past.write_text(
        "BM20A8100 Integral Calculus\nExam 7.10.2025\nCalculators are not allowed.\n"
        "1. Compute the integral\n2. (a) Find the volume\n",
        encoding="utf-8",
    )
    result = estimate_documents([past])
    assert result.docs[0].kind == "past exam"
    assert result.hours == 3.0


def test_cheat_sheet_with_exam_in_name_is_not_a_past_exam(tmp_path):
    sheet = tmp_path / "Matrix_Algebra_Exam_Sheet_2026.txt"
    sheet.write_text("1. Vector space\n2. Independence, basis, dimension\n", encoding="utf-8")
    doc = estimate_documents([sheet]).docs[0]
    assert doc.kind == "reference"
    assert doc.exercises == 0


def test_numbered_tasks_counted_once_even_in_bilingual_exams(tmp_path):
    sheet = tmp_path / "week3.txt"
    sheet.write_text(
        "1. Let A be a matrix\n2. (a) Show that U + W is a subspace\n3.(b) Prove it\n"
        "1. Olkoon A matriisi\n2. Osoita\n",
        encoding="utf-8",
    )
    assert estimate_documents([sheet]).docs[0].exercises == 3


def test_solutions_count_half_the_exercise_time(tmp_path):
    sol = tmp_path / "Week1Solutions.txt"
    sol.write_text("1. Posterior\n2. Likelihood\n3. Prior\n", encoding="utf-8")
    result = estimate_documents([sol], category="statistics")
    assert result.docs[0].kind == "solutions"
    assert result.hours == 0.5  # 3 exercises x 20 min x 0.5


def test_unsupported_files_are_skipped(tmp_path):
    notes = tmp_path / "notes.txt"
    notes.write_text("probability distribution", encoding="utf-8")
    photo = tmp_path / "IMG_0168.PNG"
    photo.write_bytes(b"\x89PNG")
    result = estimate_documents([notes, photo])
    assert result.skipped == ["IMG_0168.PNG"]
    assert len(result.docs) == 1


def test_function_and_model_do_not_make_math_look_like_programming():
    text = "Show that the linear mapping is injective. Prove the kernel is a subspace. Let f be a function."
    assert classify(text)[0] == "math_proof"
    assert classify("posterior and prior of the model, likelihood")[0] == "statistics"
