"""WSGI config for the MatStat Exam project."""
import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statlab_exam.settings")

application = get_wsgi_application()
