"""Celery application for English Study LMS."""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "english_study.settings.development")

app = Celery("english_study")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
