"""Root URL configuration for the MatStat Exam project."""
from django.urls import include, path


urlpatterns = [
    path("", include("statlab_exam.urls")),
]
