"""Forms used by the MatStat Exam project."""
from django import forms

from statlab_exam import question_store, topic_content


class QuizForm(forms.Form):
    """Dynamic form that renders one answer field for each question."""

    def __init__(self, questions, *args, **kwargs):
        """Create fields from a list of question dictionaries."""
        super().__init__(*args, **kwargs)
        for question in questions:
            field_name = f"answer_{question['id']}"
            choices = [(str(index), option) for index, option in enumerate(question["options"])]
            self.fields[field_name] = forms.ChoiceField(
                label=question["question"],
                choices=choices,
                widget=forms.RadioSelect,
                error_messages={"required": "Выберите один вариант ответа."},
            )


class QuestionForm(forms.Form):
    """Form for creating and editing question bank entries."""

    topic = forms.ChoiceField(
        label="Тема",
        choices=topic_content.get_topic_choices(),
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Выберите тему вопроса."},
    )
    question = forms.CharField(
        label="Текст вопроса",
        min_length=12,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        error_messages={
            "required": "Введите текст вопроса.",
            "min_length": "Текст вопроса должен содержать минимум 12 символов.",
        },
    )
    option_a = forms.CharField(
        label="Вариант A",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={"required": "Введите вариант A."},
    )
    option_b = forms.CharField(
        label="Вариант B",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={"required": "Введите вариант B."},
    )
    option_c = forms.CharField(
        label="Вариант C",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={"required": "Введите вариант C."},
    )
    option_d = forms.CharField(
        label="Вариант D",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={"required": "Введите вариант D."},
    )
    correct_answer = forms.IntegerField(
        label="Правильный ответ (1-4)",
        min_value=1,
        max_value=4,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "4"}),
        error_messages={
            "required": "Укажите номер правильного ответа.",
            "min_value": "Допустимы только значения от 1 до 4.",
            "max_value": "Допустимы только значения от 1 до 4.",
        },
    )
    explanation = forms.CharField(
        label="Пояснение к ответу",
        min_length=15,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        error_messages={
            "required": "Добавьте короткое пояснение.",
            "min_length": "Пояснение должно содержать минимум 15 символов.",
        },
    )
    is_exam = forms.BooleanField(
        label="Включать вопрос в итоговый экзамен",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, question_id=None, **kwargs):
        """Store current question id to support uniqueness checks on edit."""
        self.question_id = question_id
        super().__init__(*args, **kwargs)

    def clean_question(self):
        """Validate that question text stays unique within the bank."""
        question_text = self.cleaned_data["question"].strip()
        if question_store.question_exists(question_text, exclude_id=self.question_id):
            raise forms.ValidationError("Вопрос с таким текстом уже есть в банке.")
        return question_text

    def clean(self):
        """Validate answer options after field-level checks."""
        cleaned_data = super().clean()
        options = [
            cleaned_data.get("option_a", "").strip(),
            cleaned_data.get("option_b", "").strip(),
            cleaned_data.get("option_c", "").strip(),
            cleaned_data.get("option_d", "").strip(),
        ]

        normalized_options = [option.lower() for option in options if option]
        if len(normalized_options) == 4 and len(set(normalized_options)) != 4:
            raise forms.ValidationError("Все варианты ответа должны отличаться друг от друга.")

        return cleaned_data
