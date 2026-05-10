from django.db import transaction
from django.db.models import Avg, Count, Min, F

from apps.progress.models import LessonProgress


class TeacherService:
    @staticmethod
    def override_lesson_progress(teacher, student_id, lesson_id, status, score=None, note=""):
        with transaction.atomic():
            lp, created = LessonProgress.objects.select_for_update().get_or_create(
                user_id=student_id,
                lesson_id=lesson_id,
                defaults={
                    "status": status,
                    "best_score": score,
                    "attempts_count": 1,
                },
            )

            if not created:
                lp.status = status
                if score is not None:
                    lp.best_score = score
                lp.save(update_fields=["status", "best_score"])

            return lp

    @staticmethod
    def get_stuck_points(course_id, threshold_score=60):
        return (
            LessonProgress.objects.filter(
                lesson__chapter__course_id=course_id,
                status="completed",
                best_score__isnull=False,
            )
            .values(
                "lesson_id",
                lesson_title=F("lesson__title"),
                chapter_title=F("lesson__chapter__title"),
                lesson_order=F("lesson__order"),
                chapter_order=F("lesson__chapter__order"),
            )
            .annotate(
                avg_score=Avg("best_score"),
                attempts=Count("id"),
                min_score=Min("best_score"),
            )
            .filter(avg_score__lt=threshold_score)
            .order_by("chapter_order", "lesson_order")
        )
