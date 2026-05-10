"""Celery application for English Study LMS."""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "english_study.settings.development")

app = Celery("english_study")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.task_routes = {
    "apps.ai.tasks.*": {"queue": "ai_grading"},
}

app.conf.broker_transport_options = {
    "max_retries": 3,
    "interval_start": 0,
    "interval_step": 0.2,
    "interval_max": 0.2,
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
