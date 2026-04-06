"""Helpers for reading and writing questions stored in JSON."""
from __future__ import annotations

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = BASE_DIR / "data" / "questions.json"


def load_questions():
    """Load all questions from the JSON file."""
    if not QUESTIONS_FILE.exists():
        return []

    try:
        with QUESTIONS_FILE.open("r", encoding="utf-8") as file_obj:
            questions = json.load(file_obj)
    except json.JSONDecodeError:
        return []

    return sorted(questions, key=lambda item: item["id"])


def save_questions(questions):
    """Write the full question list back to JSON storage."""
    with QUESTIONS_FILE.open("w", encoding="utf-8") as file_obj:
        json.dump(questions, file_obj, ensure_ascii=False, indent=2)


def get_question_by_id(question_id):
    """Return one question by identifier."""
    for question in load_questions():
        if question["id"] == question_id:
            return question
    return None


def get_questions_by_topic(topic_slug):
    """Return all questions that belong to the selected topic."""
    return [item for item in load_questions() if item["topic"] == topic_slug]


def get_exam_questions():
    """Return questions that should appear in the final exam."""
    return [item for item in load_questions() if item.get("is_exam", True)]


def list_questions(topic_slug="", search_query="", exam_filter="all"):
    """Return questions filtered for the question bank page."""
    search_text = search_query.strip().lower()
    questions = load_questions()

    if topic_slug:
        questions = [item for item in questions if item["topic"] == topic_slug]

    if search_text:
        questions = [item for item in questions if search_text in item["question"].lower()]

    if exam_filter == "final":
        questions = [item for item in questions if item.get("is_exam", True)]
    elif exam_filter == "practice":
        questions = [item for item in questions if not item.get("is_exam", True)]

    return questions


def get_topic_counts():
    """Return a mapping with question counts by topic."""
    counts = {}
    for question in load_questions():
        counts[question["topic"]] = counts.get(question["topic"], 0) + 1
    return counts


def question_exists(question_text, exclude_id=None):
    """Check whether a question with the same text already exists."""
    normalized_text = question_text.strip().lower()
    for question in load_questions():
        same_text = question["question"].strip().lower() == normalized_text
        same_record = exclude_id is not None and question["id"] == exclude_id
        if same_text and not same_record:
            return True
    return False


def add_question(question_data):
    """Append a new question to JSON storage and return its identifier."""
    questions = load_questions()
    next_id = max((item["id"] for item in questions), default=0) + 1
    question_to_save = {"id": next_id, **question_data}
    questions.append(question_to_save)
    save_questions(questions)
    return next_id


def update_question(question_id, question_data):
    """Replace an existing question with new content."""
    questions = load_questions()
    updated_questions = []
    for question in questions:
        if question["id"] == question_id:
            updated_questions.append({"id": question_id, **question_data})
        else:
            updated_questions.append(question)
    save_questions(updated_questions)


def delete_question(question_id):
    """Remove a question from JSON storage."""
    questions = [item for item in load_questions() if item["id"] != question_id]
    save_questions(questions)
