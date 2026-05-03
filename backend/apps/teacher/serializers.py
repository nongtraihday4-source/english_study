"""
apps/teacher/serializers.py
Serializers for the Teacher Portal API.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.progress.models import SpeakingSubmission, WritingSubmission, UserEnrollment

User = get_user_model()


class TeacherUserMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "current_level"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class SpeakingSubmissionTeacherSerializer(serializers.ModelSerializer):
    student = TeacherUserMiniSerializer(source="user", read_only=True)
    type = serializers.SerializerMethodField()
    exercise_title = serializers.SerializerMethodField()

    class Meta:
        model = SpeakingSubmission
        fields = [
            "id", "student", "type", "exercise_id", "exercise_title",
            "status", "audio_s3_key", "audio_duration_seconds",
            "transcript", "target_sentence",
            "ai_score", "score_pronunciation", "score_fluency",
            "score_intonation", "score_vocabulary", "feedback_vi",
            "submitted_at", "graded_at",
        ]

    def get_type(self, obj):
        return "speaking"

    def get_exercise_title(self, obj):
        from apps.exercises.models import SpeakingExercise
        try:
            return SpeakingExercise.objects.get(pk=obj.exercise_id).title
        except SpeakingExercise.DoesNotExist:
            return f"Speaking #{obj.exercise_id}"


class WritingSubmissionTeacherSerializer(serializers.ModelSerializer):
    student = TeacherUserMiniSerializer(source="user", read_only=True)
    type = serializers.SerializerMethodField()
    exercise_title = serializers.SerializerMethodField()

    class Meta:
        model = WritingSubmission
        fields = [
            "id", "student", "type", "exercise_id", "exercise_title",
            "status", "content_text", "word_count",
            "ai_score", "score_task_achievement", "score_grammar",
            "score_vocabulary", "score_coherence", "feedback_text",
            "submitted_at", "graded_at",
        ]

    def get_type(self, obj):
        return "writing"

    def get_exercise_title(self, obj):
        from apps.exercises.models import WritingExercise
        try:
            return WritingExercise.objects.get(pk=obj.exercise_id).title
        except WritingExercise.DoesNotExist:
            return f"Writing #{obj.exercise_id}"


class TeacherGradeSerializer(serializers.Serializer):
    """Payload for POST /teacher/grade/<type>/<pk>/"""
    score = serializers.IntegerField(min_value=0, max_value=100)
    feedback = serializers.CharField(allow_blank=True, default="")
    note = serializers.CharField(allow_blank=True, default="", required=False)


class StudentProgressSerializer(serializers.ModelSerializer):
    student = TeacherUserMiniSerializer(source="user", read_only=True)
    course_title = serializers.SerializerMethodField()
    course_id = serializers.IntegerField(source="course.id", read_only=True)

    class Meta:
        model = UserEnrollment
        fields = [
            "id", "student", "course_id", "course_title",
            "status", "progress_percent", "enrolled_at", "last_activity_at",
        ]

    def get_course_title(self, obj):
        return obj.course.title if obj.course_id else ""


# ─── Assignment serializers ────────────────────────────────────────────────

class ClassAssignmentSerializer(serializers.ModelSerializer):
    """Read/Write serializer for ClassAssignment."""
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    course_title  = serializers.SerializerMethodField()
    exam_set_title = serializers.SerializerMethodField()
    student_ids    = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=User.objects.all(), required=False
    )
    submission_count = serializers.SerializerMethodField()

    class Meta:
        from apps.teacher.models import ClassAssignment
        model = ClassAssignment
        fields = [
            "id", "title", "description",
            "teacher_email",
            "course", "course_title",
            "exam_set", "exam_set_title",
            "due_date", "assign_to_all",
            "student_ids",
            "is_active", "created_at",
            "submission_count",
        ]
        read_only_fields = ["id", "teacher_email", "course_title",
                            "exam_set_title", "created_at", "submission_count"]

    def get_course_title(self, obj):
        return obj.course.title if obj.course_id else ""

    def get_exam_set_title(self, obj):
        return obj.exam_set.title if obj.exam_set_id else ""

    def get_submission_count(self, obj):
        # Count ExamAttempts linked to this assignment (if the field exists)
        try:
            return obj.attempts.count()
        except Exception:
            return 0

    def create(self, validated_data):
        from apps.teacher.models import AssignmentStudent
        student_objs = validated_data.pop("student_ids", [])
        validated_data["teacher"] = self.context["request"].user
        assignment = super().create(validated_data)
        for s in student_objs:
            AssignmentStudent.objects.get_or_create(assignment=assignment, student=s)
        return assignment

    def update(self, instance, validated_data):
        from apps.teacher.models import AssignmentStudent
        student_objs = validated_data.pop("student_ids", None)
        instance = super().update(instance, validated_data)
        if student_objs is not None:
            instance.students.all().delete()
            for s in student_objs:
                AssignmentStudent.objects.get_or_create(assignment=instance, student=s)
        return instance
