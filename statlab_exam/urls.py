"""Application URL routes for MatStat Exam."""
from django.urls import path

from statlab_exam import views


urlpatterns = [
    path("", views.index, name="index"),
    path("topics/", views.topics_list, name="topics"),
    path("topics/<slug:slug>/", views.topic_detail, name="topic_detail"),
    path("quiz/topic/<slug:slug>/", views.quiz_topic, name="quiz_topic"),
    path("quiz/final/", views.quiz_final, name="quiz_final"),
    path("result/", views.result, name="result"),
    path("questions/", views.question_bank, name="question_bank"),
    path("questions/add/", views.add_question, name="add_question"),
    path("questions/<int:question_id>/edit/", views.edit_question, name="edit_question"),
    path("questions/<int:question_id>/delete/", views.delete_question, name="delete_question"),
]
