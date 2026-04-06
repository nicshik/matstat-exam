# MatStat Exam

Небольшое веб-приложение на Django для подготовки к экзамену по математической статистике.
В приложении можно повторять темы, решать тесты и запускать общий экзамен по всем вопросам.

## Автор

Шихирев Николай Николаевич

## Что умеет приложение

- показывает список тем и отдельную страницу по каждой теме;
- запускает тренировочный тест по теме;
- запускает общий экзамен по всем вопросам;
- показывает результат с процентом и пояснениями;
- позволяет добавлять, редактировать и удалять вопросы;
- хранит вопросы в JSON-файле.

## Страницы

- `/` — главная страница;
- `/topics/` — список тем;
- `/topics/<slug>/` — материал по теме;
- `/quiz/topic/<slug>/` — тест по теме;
- `/quiz/final/` — итоговый экзамен;
- `/result/` — результаты теста;
- `/questions/` — банк вопросов;
- `/questions/add/` — добавление вопроса;
- `/questions/<id>/edit/` — редактирование вопроса.

## Технологии

- Python 3
- Django
- Django templates
- Bootstrap 5 + собственные стили
- JSON для хранения вопросов
- SQLite для хранения сессий Django

## Запуск локально

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

После запуска откройте `http://127.0.0.1:8000/`.

## Проверка качества кода

```bash
PYLINTHOME=.pylint.d pylint statlab_exam
```

## Структура проекта

```text
.
├── data/questions.json
├── manage.py
├── README.md
├── requirements.txt
├── static/style.css
├── statlab_exam/
│   ├── forms.py
│   ├── question_store.py
│   ├── root_urls.py
│   ├── settings.py
│   ├── topic_content.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
└── templates/
    ├── base_page.html
    ├── index.html
    ├── question_bank.html
    ├── question_form.html
    ├── quiz.html
    ├── result.html
    ├── topic_detail.html
    └── topics.html
```
