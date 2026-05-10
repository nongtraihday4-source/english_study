"""
apps/curriculum/serializers.py
"""
from rest_framework import serializers

from utils.formatters import fmt_vn, fmt_vn_datetime
from .models import CEFRLevel, Course, Chapter, Lesson, LessonContent, LessonExercise, UnlockRule
from .schemas import LessonContentSchema


class CEFRLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CEFRLevel
        fields = ["id", "code", "name", "name_vi", "order", "is_active"]


class UnlockRuleSerializer(serializers.ModelSerializer):
    required_lesson_title = serializers.CharField(source="required_lesson.title", read_only=True)

    class Meta:
        model = UnlockRule
        fields = ["id", "required_lesson", "required_lesson_title", "min_score"]


class LessonSerializer(serializers.ModelSerializer):
    unlock_rules = UnlockRuleSerializer(many=True, read_only=True)
    progress_status = serializers.SerializerMethodField()
    exercise_type = serializers.SerializerMethodField()
    exercise_id = serializers.SerializerMethodField()
    is_unlocked = serializers.SerializerMethodField()
    chapter_id = serializers.IntegerField(source="chapter.id", read_only=True)
    course_id = serializers.IntegerField(source="chapter.course.id", read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id", "title", "lesson_type", "order", "estimated_minutes",
            "is_active", "unlock_rules", "progress_status",
            "exercise_type", "exercise_id", "is_unlocked", "chapter_id", "course_id",
        ]

    def get_exercise_type(self, obj):
        le = obj.exercises.first()
        return le.exercise_type if le else obj.lesson_type

    def get_exercise_id(self, obj):
        le = obj.exercises.first()
        return le.exercise_id if le else None

    def get_is_unlocked(self, obj):
        return self.context.get("unlock_map", {}).get(obj.id, False)

    def get_progress_status(self, obj):
        return self.context.get("progress_map", {}).get(obj.id, "locked")


class ChapterSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lesson_count = serializers.IntegerField(source="lessons.count", read_only=True)

    class Meta:
        model = Chapter
        fields = ["id", "title", "order", "passing_score", "lessons", "lesson_count"]


class CourseListSerializer(serializers.ModelSerializer):
    level = CEFRLevelSerializer(read_only=True)
    total_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "description", "level", "is_premium",
            "thumbnail", "total_lessons",
        ]

    def get_total_lessons(self, obj):
        return Lesson.objects.filter(chapter__course=obj).count()


class CourseDetailSerializer(CourseListSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()
    completed_lessons_count = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + [
            "chapters", "is_enrolled", "progress_percent",
            "completed_lessons_count", "average_score",
        ]

    def _get_enrollment(self, obj):
        """Cache enrollment lookup per serialization instance."""
        cache_key = f"_enroll_{obj.pk}"
        if cache_key not in self.__dict__:
            from apps.progress.models import UserEnrollment
            request = self.context.get("request")
            if not request or not request.user.is_authenticated:
                self.__dict__[cache_key] = None
            else:
                self.__dict__[cache_key] = UserEnrollment.objects.filter(
                    user=request.user, course=obj, is_deleted=False
                ).first()
        return self.__dict__[cache_key]

    def get_is_enrolled(self, obj):
        return self._get_enrollment(obj) is not None

    def get_progress_percent(self, obj):
        enrollment = self._get_enrollment(obj)
        return float(enrollment.progress_percent) if enrollment else 0.0

    def get_completed_lessons_count(self, obj):
        from apps.progress.models import LessonProgress
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0
        return LessonProgress.objects.filter(
            user=request.user,
            lesson__chapter__course=obj,
            status="completed",
        ).count()

    def get_average_score(self, obj):
        from apps.progress.models import LessonProgress
        from django.db.models import Avg
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        avg = LessonProgress.objects.filter(
            user=request.user,
            lesson__chapter__course=obj,
            status="completed",
            best_score__isnull=False,
        ).aggregate(avg=Avg("best_score"))["avg"]
        return round(avg) if avg is not None else None


class CourseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "title", "slug", "description", "level", "is_premium",
            "thumbnail_s3_key",
        ]


class LessonContentSerializer(serializers.ModelSerializer):
    lesson_id = serializers.IntegerField(source="lesson.id", read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    lesson_type = serializers.CharField(source="lesson.lesson_type", read_only=True)
    estimated_minutes = serializers.IntegerField(source="lesson.estimated_minutes", read_only=True)
    chapter_title = serializers.CharField(source="lesson.chapter.title", read_only=True)
    progress_status = serializers.SerializerMethodField()
    created_at_vn = serializers.SerializerMethodField()
    updated_at_vn = serializers.SerializerMethodField()

    class Meta:
        model = LessonContent
        fields = [
            "id", "lesson_id", "lesson_title", "lesson_type", "estimated_minutes",
            "chapter_title", "progress_status",
            "learning_objectives",
            "reading_passage", "reading_image_url", "reading_questions",
            "vocab_items", "vocab_word_ids",
            # New structured fields (preferred by frontend)
            "grammar_sections", "skill_sections",
            # Dedicated skill lesson content
            "listening_content", "speaking_content", "writing_content",
            # Legacy flat fields (kept for backward compat)
            "grammar_topic_id", "grammar_title", "grammar_note", "grammar_examples",
            "exercises",
            "srs_review_count", "completion_xp", "bonus_xp",
            "created_at_vn", "updated_at_vn",
        ]

    def get_progress_status(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return "locked"
        from apps.progress.models import LessonProgress
        lp = LessonProgress.objects.filter(user=request.user, lesson=obj.lesson).first()
        return lp.status if lp else "locked"

    def get_created_at_vn(self, obj):
        return fmt_vn_datetime(obj.created_at)

    def get_updated_at_vn(self, obj):
        return fmt_vn_datetime(obj.updated_at)

    def validate(self, attrs):
        allowed_fields = set(self.fields.keys())
        extra_fields = set(self.initial_data.keys()) - allowed_fields
        if extra_fields:
            raise serializers.ValidationError({"json_schema": f"Extra fields forbidden: {extra_fields}"})
        try:
            LessonContentSchema.model_validate(attrs)
        except Exception as e:
            raise serializers.ValidationError({"json_schema": str(e)})
        return attrs
