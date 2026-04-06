"""Views for the StatLab Exam Django project."""
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from statlab_exam import question_store, topic_content
from statlab_exam.forms import QuestionForm, QuizForm


def index(request):
    """Render the main page with general project statistics."""
    topic_cards = _build_topic_cards(request)
    last_result = request.session.get("last_result")
    total_attempts = sum(
        item["attempts"] for item in request.session.get("topic_progress", {}).values()
    )
    context = {
        "total_questions": len(question_store.load_questions()),
        "total_exam_questions": len(question_store.get_exam_questions()),
        "total_topics": len(topic_cards),
        "topic_cards": topic_cards,
        "last_result": last_result,
        "total_attempts": total_attempts,
    }
    return render(request, "index.html", context)


def topics_list(request):
    """Render all topic cards with optional sorting."""
    sort_mode = request.GET.get("sort", "name")
    topic_cards = _build_topic_cards(request)

    if sort_mode == "count":
        topic_cards.sort(key=lambda item: (-item["count"], item["label"]))
    elif sort_mode == "progress":
        topic_cards.sort(key=lambda item: (-item["best_percent"], item["label"]))
    else:
        topic_cards.sort(key=lambda item: item["label"])
        sort_mode = "name"

    return render(request, "topics.html", {"topics": topic_cards, "sort_mode": sort_mode})


def topic_detail(request, slug):
    """Show the theory summary for one topic."""
    topic = topic_content.get_topic(slug)
    if topic is None:
        raise Http404("Тема не найдена.")

    questions = question_store.get_questions_by_topic(slug)
    progress = request.session.get("topic_progress", {}).get(slug, {})
    sample_questions = questions[:3]
    context = {
        "topic": topic,
        "slug": slug,
        "questions_count": len(questions),
        "sample_questions": sample_questions,
        "best_percent": progress.get("best_percent", 0),
        "attempts": progress.get("attempts", 0),
    }
    return render(request, "topic_detail.html", context)


def quiz_topic(request, slug):
    """Render and validate a topic quiz."""
    topic = topic_content.get_topic(slug)
    questions = question_store.get_questions_by_topic(slug)
    if topic is None or not questions:
        return redirect("topics")

    if request.method == "POST":
        form = QuizForm(questions, request.POST)
        if form.is_valid():
            return _store_and_redirect_result(
                request,
                questions,
                form.cleaned_data,
                f"Тренировка по теме: {topic['label']}",
                progress_slug=slug,
            )
    else:
        form = QuizForm(questions)

    context = {
        "form": form,
        "page_title": topic["label"],
        "quiz_label": "Тест по теме",
        "back_url": "topic_detail",
        "back_arg": slug,
    }
    return render(request, "quiz.html", context)


def quiz_final(request):
    """Render and validate the final mixed exam."""
    questions = question_store.get_exam_questions()
    if not questions:
        return redirect("index")

    if request.method == "POST":
        form = QuizForm(questions, request.POST)
        if form.is_valid():
            return _store_and_redirect_result(
                request,
                questions,
                form.cleaned_data,
                "Итоговый экзамен по всем темам",
            )
    else:
        form = QuizForm(questions)

    context = {
        "form": form,
        "page_title": "Итоговый экзамен",
        "quiz_label": "Общий тест",
        "back_url": "index",
        "back_arg": None,
    }
    return render(request, "quiz.html", context)


def result(request):
    """Render the last saved quiz result."""
    results = request.session.get("quiz_results")
    quiz_mode = request.session.get("quiz_mode")
    if not results or not quiz_mode:
        return redirect("index")

    correct = sum(1 for item in results if item["is_correct"])
    total = len(results)
    percent = round(correct / total * 100) if total else 0
    context = {
        "results": results,
        "quiz_mode": quiz_mode,
        "correct": correct,
        "total": total,
        "percent": percent,
    }
    return render(request, "result.html", context)


def question_bank(request):
    """Show the full question bank with simple filters."""
    topic_slug = request.GET.get("topic", "")
    search_query = request.GET.get("q", "")
    exam_filter = request.GET.get("exam", "all")
    questions = question_store.list_questions(topic_slug, search_query, exam_filter)

    prepared_questions = []
    for question in questions:
        prepared_questions.append({
            **question,
            "topic_label": topic_content.TOPIC_CONTENT[question["topic"]]["label"],
            "correct_option": question["options"][question["correct_answer"]],
        })

    context = {
        "questions": prepared_questions,
        "topic_choices": topic_content.get_topic_choices(),
        "selected_topic": topic_slug,
        "search_query": search_query,
        "exam_filter": exam_filter,
        "saved_flag": request.GET.get("saved", ""),
    }
    return render(request, "question_bank.html", context)


def add_question(request):
    """Create a new question in the JSON question bank."""
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question_store.add_question(_build_question_payload(form.cleaned_data))
            return redirect("/questions/?saved=created")
    else:
        form = QuestionForm()

    context = {
        "form": form,
        "page_title": "Добавить вопрос",
        "submit_label": "Сохранить вопрос",
        "delete_allowed": False,
        "question_id": None,
    }
    return render(request, "question_form.html", context)


def edit_question(request, question_id):
    """Edit an existing question bank entry."""
    question = question_store.get_question_by_id(question_id)
    if question is None:
        raise Http404("Вопрос не найден.")

    if request.method == "POST":
        form = QuestionForm(request.POST, question_id=question_id)
        if form.is_valid():
            question_store.update_question(question_id, _build_question_payload(form.cleaned_data))
            return redirect("/questions/?saved=updated")
    else:
        form = QuestionForm(initial=_question_to_initial(question), question_id=question_id)

    context = {
        "form": form,
        "page_title": "Редактировать вопрос",
        "submit_label": "Обновить вопрос",
        "delete_allowed": True,
        "question_id": question_id,
    }
    return render(request, "question_form.html", context)


@require_POST
def delete_question(_request, question_id):
    """Delete a question from the bank."""
    if question_store.get_question_by_id(question_id) is not None:
        question_store.delete_question(question_id)
    return redirect("/questions/?saved=deleted")


def _build_topic_cards(request):
    """Prepare topic cards with counts and progress from session."""
    counts = question_store.get_topic_counts()
    progress_map = request.session.get("topic_progress", {})
    cards = []
    for slug, item in topic_content.TOPIC_CONTENT.items():
        progress = progress_map.get(slug, {})
        cards.append({
            "slug": slug,
            "label": item["label"],
            "short_description": item["short_description"],
            "count": counts.get(slug, 0),
            "attempts": progress.get("attempts", 0),
            "best_percent": progress.get("best_percent", 0),
        })
    return cards


def _store_and_redirect_result(request, questions, cleaned_data, quiz_mode, progress_slug=None):
    """Evaluate quiz answers, store the result in session and redirect."""
    results = _evaluate_answers(cleaned_data, questions)
    correct = sum(1 for item in results if item["is_correct"])
    total = len(results)
    percent = round(correct / total * 100) if total else 0

    request.session["quiz_results"] = results
    request.session["quiz_mode"] = quiz_mode
    request.session["last_result"] = {
        "mode": quiz_mode,
        "correct": correct,
        "total": total,
        "percent": percent,
    }
    if progress_slug:
        _update_topic_progress(request, progress_slug, percent)

    return redirect("result")


def _evaluate_answers(cleaned_data, questions):
    """Compare user answers with the correct ones and build result rows."""
    results = []
    for question in questions:
        user_answer = int(cleaned_data[f"answer_{question['id']}"])
        topic = topic_content.TOPIC_CONTENT[question["topic"]]
        results.append({
            "question": question["question"],
            "options": question["options"],
            "user_answer": user_answer,
            "correct_answer": question["correct_answer"],
            "is_correct": user_answer == question["correct_answer"],
            "explanation": question["explanation"],
            "topic_label": topic["label"],
        })
    return results


def _update_topic_progress(request, slug, percent):
    """Save per-topic progress in the user session."""
    progress_map = request.session.get("topic_progress", {})
    current_data = progress_map.get(slug, {"attempts": 0, "best_percent": 0})
    current_data["attempts"] += 1
    current_data["best_percent"] = max(current_data["best_percent"], percent)
    progress_map[slug] = current_data
    request.session["topic_progress"] = progress_map


def _build_question_payload(cleaned_data):
    """Convert validated form data to JSON storage format."""
    return {
        "topic": cleaned_data["topic"],
        "question": cleaned_data["question"].strip(),
        "options": [
            cleaned_data["option_a"].strip(),
            cleaned_data["option_b"].strip(),
            cleaned_data["option_c"].strip(),
            cleaned_data["option_d"].strip(),
        ],
        "correct_answer": cleaned_data["correct_answer"] - 1,
        "explanation": cleaned_data["explanation"].strip(),
        "is_exam": cleaned_data["is_exam"],
    }


def _question_to_initial(question):
    """Prepare initial values for the edit form."""
    return {
        "topic": question["topic"],
        "question": question["question"],
        "option_a": question["options"][0],
        "option_b": question["options"][1],
        "option_c": question["options"][2],
        "option_d": question["options"][3],
        "correct_answer": question["correct_answer"] + 1,
        "explanation": question["explanation"],
        "is_exam": question.get("is_exam", True),
    }
