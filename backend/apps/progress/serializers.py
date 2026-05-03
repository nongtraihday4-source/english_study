"""
apps/progress/serializers.py
"""
import logging

from rest_framework import serializers

from utils.formatters import fmt_percent, fmt_score
from .models import (
    UserEnrollment,
    LessonProgress,
    ExerciseResult,
    SpeakingSubmission,
    WritingSubmission,
    DailyStreak,
    CumulativeScore,
)

logger = logging.getLogger("es.progress")


class UserEnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    course_level_code = serializers.CharField(source="course.level.code", read_only=True, default="")
    progress_display = serializers.SerializerMethodField()

    class Meta:
        model = UserEnrollment
        fields = [
            "id", "course", "course_title", "course_level_code", "progress_percent",
            "progress_display", "enrolled_at", "completed_at",
        ]
        read_only_fields = ["id", "enrolled_at", "completed_at", "progress_percent"]

    def get_progress_display(self, obj):
        return fmt_percent(obj.progress_percent)


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    best_score_display = serializers.SerializerMethodField()

    class Meta:
        model = LessonProgress
        fields = [
            "id", "lesson", "lesson_title", "status", "best_score",
            "best_score_display", "attempts_count", "updated_at", "completed_at",
        ]
        read_only_fields = ["__all__"]

    def get_best_score_display(self, obj):
        return fmt_score(obj.best_score) if obj.best_score is not None else None


# ── Submission inputs ─────────────────────────────────────────────────────────

class SubmitListeningSerializer(serializers.Serializer):
    """POST body for submitting listening answers."""
    lesson_id = serializers.IntegerField()
    exercise_id = serializers.IntegerField()
    answers = serializers.DictField(
        child=serializers.JSONField(),
        help_text='{"question_id": answer_value, ...}',
    )
    time_spent_seconds = serializers.IntegerField(min_value=0, default=0)


class SubmitReadingSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField()
    exercise_id = serializers.IntegerField()
    answers = serializers.DictField(child=serializers.JSONField())
    time_spent_seconds = serializers.IntegerField(min_value=0, default=0)


class SubmitSpeakingSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField()
    exercise_id = serializers.IntegerField()
    # Production: client uploads to S3 and sends the key
    audio_s3_key = serializers.CharField(max_length=500, required=False, allow_null=True,
                                          help_text="S3 key (production) — or omit when uploading audio_file directly")
    # Dev/fallback: client sends raw audio file via multipart
    audio_file = serializers.FileField(required=False, allow_null=True)
    target_sentence = serializers.CharField(max_length=500)


class SubmitWritingSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField()
    exercise_id = serializers.IntegerField()
    content_text = serializers.CharField(min_length=20)

    def validate_content_text(self, value):
        word_count = len(value.split())
        if word_count < 20:
            raise serializers.ValidationError("Bài viết quá ngắn (tối thiểu 20 từ để nộp).")
        return value


class SubmitExamSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    lesson_id = serializers.IntegerField(required=False, allow_null=True)
    answers = serializers.DictField(
        child=serializers.JSONField(),
        help_text='{"question_id": answer_value, ...}',
    )
    time_spent_seconds = serializers.IntegerField(min_value=0, default=0)


# ── Result outputs ────────────────────────────────────────────────────────────

class ExerciseResultSerializer(serializers.ModelSerializer):
    score_display = serializers.SerializerMethodField()
    course_id = serializers.SerializerMethodField()
    next_lesson_id = serializers.SerializerMethodField()
    next_exercise_type = serializers.SerializerMethodField()
    next_exercise_id = serializers.SerializerMethodField()
    chapter_completed = serializers.SerializerMethodField()
    chapter_id = serializers.SerializerMethodField()
    chapter_title = serializers.SerializerMethodField()
    chapter_avg_score = serializers.SerializerMethodField()

    class Meta:
        model = ExerciseResult
        fields = [
            "id", "exercise_type", "exercise_id", "score", "score_display",
            "passed", "detail_json", "created_at",
            "course_id",
            "next_lesson_id", "next_exercise_type", "next_exercise_id",
            "chapter_completed", "chapter_id", "chapter_title", "chapter_avg_score",
        ]

    def get_score_display(self, obj):
        return fmt_score(obj.score)

    def _resolve_next_lesson(self, obj):
        """
        Compute and cache the next available Lesson object on `obj`.
        Returns a Lesson instance or None.
        """
        if hasattr(obj, "_next_lesson_cache"):
            return obj._next_lesson_cache
        if not obj.lesson_id:
            obj._next_lesson_cache = None
            return None
        try:
            from apps.curriculum.models import Lesson
            lesson = obj.lesson
            next_lesson = (
                Lesson.objects.filter(
                    chapter_id=lesson.chapter_id,
                    order__gt=lesson.order,
                    is_active=True,
                )
                .order_by("order")
                .first()
            )
            obj._next_lesson_cache = next_lesson
        except Exception as exc:
            logger.warning("Failed to resolve next_lesson for result=%s: %s", obj.pk, exc)
            obj._next_lesson_cache = None
        return obj._next_lesson_cache

    def get_course_id(self, obj):
        try:
            return obj.lesson.chapter.course_id if obj.lesson_id else None
        except Exception:
            return None

    def get_next_lesson_id(self, obj):
        next_lesson = self._resolve_next_lesson(obj)
        return next_lesson.pk if next_lesson else None

    def get_next_exercise_type(self, obj):
        """Return the exercise_type of the first LessonExercise in the next lesson."""
        next_lesson = self._resolve_next_lesson(obj)
        if not next_lesson:
            return None
        le = next_lesson.lessonexercise_set.order_by("order").first()
        return le.exercise_type if le else next_lesson.lesson_type

    def get_next_exercise_id(self, obj):
        """Return the exercise_id of the first LessonExercise in the next lesson."""
        next_lesson = self._resolve_next_lesson(obj)
        if not next_lesson:
            return None
        le = next_lesson.lessonexercise_set.order_by("order").first()
        return le.exercise_id if le else None

    def _get_chapter_info(self, obj):
        return getattr(obj, "_chapter_info", {})

    def get_chapter_completed(self, obj):
        return self._get_chapter_info(obj).get("chapter_completed", False)

    def get_chapter_id(self, obj):
        return self._get_chapter_info(obj).get("chapter_id")

    def get_chapter_title(self, obj):
        return self._get_chapter_info(obj).get("chapter_title")

    def get_chapter_avg_score(self, obj):
        return self._get_chapter_info(obj).get("chapter_avg_score")


class SpeakingSubmissionSerializer(serializers.ModelSerializer):
    ai_score_display = serializers.SerializerMethodField()
    course_id = serializers.SerializerMethodField()
    next_lesson_id = serializers.SerializerMethodField()
    next_exercise_type = serializers.SerializerMethodField()
    next_exercise_id = serializers.SerializerMethodField()
    chapter_completed = serializers.SerializerMethodField()
    chapter_id = serializers.SerializerMethodField()
    chapter_title = serializers.SerializerMethodField()
    chapter_avg_score = serializers.SerializerMethodField()

    class Meta:
        model = SpeakingSubmission
        fields = [
            "id", "exercise_id", "status",
            "transcript",
            "ai_score", "ai_score_display",
            "score_pronunciation", "score_fluency", "score_intonation", "score_vocabulary",
            "error_list_json", "submitted_at",
            "course_id", "next_lesson_id", "next_exercise_type", "next_exercise_id",
            "chapter_completed", "chapter_id", "chapter_title", "chapter_avg_score",
        ]
        read_only_fields = ["__all__"]

    def get_ai_score_display(self, obj):
        return fmt_score(obj.ai_score) if obj.ai_score is not None else "Đang chấm..."

    def _resolve_next_lesson(self, obj):
        if hasattr(obj, "_next_lesson_cache"):
            return obj._next_lesson_cache
        if not obj.lesson_id:
            obj._next_lesson_cache = None
            return None
        try:
            from apps.curriculum.models import Lesson
            lesson = obj.lesson
            obj._next_lesson_cache = (
                Lesson.objects.filter(chapter_id=lesson.chapter_id, order__gt=lesson.order, is_active=True)
                .order_by("order")
                .first()
            )
        except Exception:
            obj._next_lesson_cache = None
        return obj._next_lesson_cache

    def _get_chapter_info(self, obj):
        if hasattr(obj, "_chapter_info_cache"):
            return obj._chapter_info_cache
        if not obj.lesson_id or obj.status != "completed":
            obj._chapter_info_cache = {"chapter_completed": False}
            return obj._chapter_info_cache
        try:
            from .grading import _check_chapter_completion
            obj._chapter_info_cache = _check_chapter_completion(obj.user, obj.lesson)
        except Exception:
            obj._chapter_info_cache = {"chapter_completed": False}
        return obj._chapter_info_cache

    def get_course_id(self, obj):
        try:
            return obj.lesson.chapter.course_id if obj.lesson_id else None
        except Exception:
            return None

    def get_next_lesson_id(self, obj):
        next_lesson = self._resolve_next_lesson(obj)
        return next_lesson.pk if next_lesson else None

    def get_next_exercise_type(self, obj):
        next_lesson = self._resolve_next_lesson(obj)
        if not next_lesson:
            return None
        le = next_lesson.lessonexercise_set.order_by("order").first()
        return le.exercise_type if le else next_lesson.lesson_type

    def get_next_exercise_id(self, obj):
        next_lesson = self._resolve_next_lesson(obj)
        if not next_lesson:
            return None
        le = next_lesson.lessonexercise_set.order_by("order").first()
        return le.exercise_id if le else None

    def get_chapter_completed(self, obj):
        return self._get_chapter_info(obj).get("chapter_completed", False)

    def get_chapter_id(self, obj):
        return self._get_chapter_info(obj).get("chapter_id")

    def get_chapter_title(self, obj):
        return self._get_chapter_info(obj).get("chapter_title")

    def get_chapter_avg_score(self, obj):
        return self._get_chapter_info(obj).get("chapter_avg_score")


class WritingSubmissionSerializer(serializers.ModelSerializer):
    ai_score_display = serializers.SerializerMethodField()
    course_id = serializers.SerializerMethodField()
    next_lesson_id = serializers.SerializerMethodField()
    next_exercise_type = serializers.SerializerMethodField()
    next_exercise_id = serializers.SerializerMethodField()
    chapter_completed = serializers.SerializerMethodField()
    chapter_id = serializers.SerializerMethodField()
    chapter_title = serializers.SerializerMethodField()
    chapter_avg_score = serializers.SerializerMethodField()

    class Meta:
        model = WritingSubmission
        fields = [
            "id", "exercise_id", "status", "word_count",
            "ai_score", "ai_score_display",
            "score_task_achievement", "score_grammar", "score_vocabulary", "score_coherence",
            "feedback_text", "error_list_json", "vocab_cefr_json", "teacher_comment",
            "submitted_at",
            "course_id", "next_lesson_id", "next_exercise_type", "next_exercise_id",
            "chapter_completed", "chapter_id", "chapter_title", "chapter_avg_score",
        ]
        read_only_fields = ["__all__"]

    def get_ai_score_display(self, obj):
        return fmt_score(obj.ai_score) if obj.ai_score is not None else "Đang chấm..."

    def _resolve_next_lesson(self, obj):
        if hasattr(obj, "_next_lesson_cache"):
            return obj._next_lesson_cache
        if not obj.lesson_id:
            obj._next_lesson_cache = None
            return None
        try:
            from apps.curriculum.models import Lesson
            lesson = obj.lesson
            obj._next_lesson_cache = (
                Lesson.objects.filter(chapter_id=lesson.chapter_id, order__gt=lesson.order, is_active=True)
                .order_by("order")
                .first()
            )
        except Exception:
            obj._next_lesson_cache = None
        return obj._next_lesson_cache

    def _get_chapter_info(self, obj):
        if hasattr(obj, "_chapter_info_cache"):
            return obj._chapter_info_cache
        if not obj.lesson_id or obj.status != "completed":
            obj._chapter_info_cache = {"chapter_completed": False}
            return obj._chapter_info_cache
        try:
            from .grading import _check_chapter_completion
            obj._chapter_info_cache = _check_chapter_completion(obj.user, obj.lesson)
        except Exception:
            obj._chapter_info_cache = {"chapter_completed": False}
        return obj._chapter_info_cache

    def get_course_id(self, obj):
        try:
            return obj.lesson.chapter.course_id if obj.lesson_id else None
        except Exception:
            return None

    def get_next_lesson_id(self, obj):
        next_lesson = self._resolve_next_lesson(obj)
        return next_lesson.pk if next_lesson else None

    def get_next_exercise_type(self, obj):
        next_lesson = self._resolve_next_lesson(obj)
        if not next_lesson:
            return None
        le = next_lesson.lessonexercise_set.order_by("order").first()
        return le.exercise_type if le else next_lesson.lesson_type

    def get_next_exercise_id(self, obj):
        next_lesson = self._resolve_next_lesson(obj)
        if not next_lesson:
            return None
        le = next_lesson.lessonexercise_set.order_by("order").first()
        return le.exercise_id if le else None

    def get_chapter_completed(self, obj):
        return self._get_chapter_info(obj).get("chapter_completed", False)

    def get_chapter_id(self, obj):
        return self._get_chapter_info(obj).get("chapter_id")

    def get_chapter_title(self, obj):
        return self._get_chapter_info(obj).get("chapter_title")

    def get_chapter_avg_score(self, obj):
        return self._get_chapter_info(obj).get("chapter_avg_score")


class DailyStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStreak
        fields = [
            "current_streak", "longest_streak",
            "last_activity_date", "streak_protected_until",
        ]


class CumulativeScoreSerializer(serializers.ModelSerializer):
    level_code = serializers.CharField(source="level.code", read_only=True)
    overall_display = serializers.SerializerMethodField()

    class Meta:
        model = CumulativeScore
        fields = [
            "level_code", "listening_avg", "speaking_avg", "reading_avg", "writing_avg",
            "overall_avg", "overall_display", "total_exercises_done", "cefr_equivalent",
        ]

    def get_overall_display(self, obj):
        return fmt_percent(obj.overall_avg)


class DashboardStatsSerializer(serializers.Serializer):
    """Composite serializer for GET /api/dashboard/."""
    streak = DailyStreakSerializer()
    cumulative_scores = CumulativeScoreSerializer(many=True)
    enrolled_courses = UserEnrollmentSerializer(many=True)
    recent_results = ExerciseResultSerializer(many=True)
    total_xp = serializers.IntegerField()
    total_xp_display = serializers.CharField()
