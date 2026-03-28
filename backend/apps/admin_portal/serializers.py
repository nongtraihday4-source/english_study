"""
apps/admin_portal/serializers.py
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.curriculum.models import CEFRLevel, Course, Chapter, Lesson
from apps.payments.models import Coupon, CouponRedemption, PaymentTransaction, SubscriptionPlan, UserSubscription
from apps.exercises.models import ExamSet, ListeningExercise, ReadingExercise, SpeakingExercise, WritingExercise
from apps.progress.models import AIGradingJob, SpeakingSubmission, WritingSubmission
from apps.gamification.models import Achievement, Certificate, LeaderboardSnapshot, XPLog
from apps.notifications.models import Notification, NotificationTemplate
from .models import AuditLog, StaffPermission, SystemSetting

User = get_user_model()


class AdminCourseSerializer(serializers.ModelSerializer):
    cefr_level = serializers.CharField(source="level.code", read_only=True)
    level_name = serializers.CharField(source="level.name_vi", read_only=True)
    level = serializers.PrimaryKeyRelatedField(
        queryset=CEFRLevel.objects.filter(is_active=True), write_only=True
    )
    student_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "description", "cefr_level", "level_name",
            "level", "order", "is_premium", "is_active",
            "student_count", "created_at",
        ]
        read_only_fields = ["id", "created_at", "student_count"]


class AdminChapterSerializer(serializers.ModelSerializer):
    lesson_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Chapter
        fields = ["id", "title", "order", "passing_score", "lesson_count"]
        read_only_fields = ["id"]


class AdminLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "order", "lesson_type", "is_active", "estimated_minutes"]
        read_only_fields = ["id"]


# ── Payments ───────────────────────────────────────────────────────────────────

class AdminPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            "id", "name", "name_vi", "billing_period", "price_vnd", "price_usd",
            "original_price_vnd", "features_json", "max_lessons_per_day",
            "is_active", "sort_order", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AdminCouponSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan_restriction.name_vi", read_only=True, default=None)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coupon
        fields = [
            "id", "code", "discount_type", "discount_value", "max_uses", "used_count",
            "plan_restriction", "plan_name", "valid_from", "expires_at",
            "is_active", "min_purchase_vnd", "is_available", "created_at",
        ]
        read_only_fields = ["id", "used_count", "created_at", "is_available"]


class AdminTransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    plan_name = serializers.CharField(source="plan.name_vi", read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            "id", "user_email", "plan_name", "gateway", "amount_vnd",
            "original_amount_vnd", "discount_vnd", "status",
            "gateway_txn_id", "ip_address", "created_at", "updated_at",
        ]
        read_only_fields = fields


class AdminSubscriptionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    plan_name = serializers.CharField(source="plan.name_vi", read_only=True)
    is_premium = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            "id", "user_email", "plan_name", "status", "started_at",
            "expires_at", "auto_renew", "is_premium", "updated_at",
        ]
        read_only_fields = ["id", "user_email", "plan_name", "is_premium", "updated_at"]


# ── Assessments ────────────────────────────────────────────────────────────────

class AdminExamSetSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source="created_by.email", read_only=True, default=None)

    class Meta:
        model = ExamSet
        fields = [
            "id", "title", "exam_type", "skill", "cefr_level", "time_limit_minutes",
            "passing_score", "total_questions", "structure_json",
            "is_active", "created_by_email", "created_at",
        ]
        read_only_fields = ["id", "created_by_email", "created_at"]


class AdminListeningExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningExercise
        fields = ["id", "title", "cefr_level", "audio_duration_seconds", "max_plays", "created_at"]
        read_only_fields = ["id", "created_at"]


class AdminSpeakingExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeakingExercise
        fields = ["id", "title", "cefr_level", "time_limit_seconds", "created_at"]
        read_only_fields = ["id", "created_at"]


class AdminReadingExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingExercise
        fields = ["id", "title", "cefr_level", "time_limit_seconds", "created_at"]
        read_only_fields = ["id", "created_at"]


class AdminWritingExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingExercise
        fields = ["id", "title", "cefr_level", "min_words", "max_words", "time_limit_minutes", "created_at"]
        read_only_fields = ["id", "created_at"]


# ── AI Grading ─────────────────────────────────────────────────────────────────

class AdminGradingJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIGradingJob
        fields = [
            "id", "job_type", "submission_id", "status", "retry_count",
            "error_message", "ai_model_used", "tokens_used",
            "queued_at", "started_at", "completed_at",
        ]
        read_only_fields = fields


class AdminSpeakingSubmissionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = SpeakingSubmission
        fields = [
            "id", "user_email", "exercise_id", "status", "ai_score",
            "score_pronunciation", "score_fluency", "score_intonation", "score_vocabulary",
            "transcript", "target_sentence", "feedback_vi", "error_list_json",
            "submitted_at", "graded_at",
        ]
        read_only_fields = fields


class AdminWritingSubmissionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = WritingSubmission
        fields = [
            "id", "user_email", "exercise_id", "status", "ai_score", "word_count",
            "score_task_achievement", "score_grammar", "score_vocabulary", "score_coherence",
            "content_text", "feedback_text", "error_list_json", "vocab_cefr_json",
            "teacher_comment", "submitted_at", "graded_at",
        ]
        read_only_fields = [
            "id", "user_email", "exercise_id", "status", "ai_score", "word_count",
            "score_task_achievement", "score_grammar", "score_vocabulary", "score_coherence",
            "content_text", "feedback_text", "error_list_json", "vocab_cefr_json",
            "submitted_at", "graded_at",
        ]


# ── Gamification ───────────────────────────────────────────────────────────────

class AdminAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = [
            "id", "name", "name_vi", "description", "category",
            "condition_type", "threshold_value", "icon_emoji",
            "xp_reward", "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AdminCertificateSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    level_code = serializers.CharField(source="level.code", read_only=True, default=None)
    course_title = serializers.CharField(source="course.title", read_only=True, default=None)

    class Meta:
        model = Certificate
        fields = [
            "id", "user_email", "level_code", "course_title",
            "verification_code", "issued_at", "is_valid",
        ]
        read_only_fields = fields


class AdminXPLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = XPLog
        fields = ["id", "user_email", "source", "xp_amount", "note", "created_at"]
        read_only_fields = fields


# ── Notifications ──────────────────────────────────────────────────────────────

class AdminNotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            "notification_type", "title_vi", "message_template_vi", "push_enabled",
        ]


class AdminNotificationHistorySerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id", "user_email", "notification_type", "title", "message",
            "is_read", "created_at",
        ]
        read_only_fields = fields


# ── Staff Permissions ──────────────────────────────────────────────────────────

class AdminStaffPermissionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email

    class Meta:
        model = StaffPermission
        fields = [
            "user_email", "user_name",
            "manage_users", "manage_content", "manage_payments",
            "manage_assessments", "manage_notifications", "manage_gamification",
            "view_analytics", "manage_settings", "view_audit_log",
            "updated_at",
        ]
        read_only_fields = ["user_email", "user_name", "updated_at"]


# ── Audit Log ──────────────────────────────────────────────────────────────────

class AdminAuditLogSerializer(serializers.ModelSerializer):
    admin_email = serializers.CharField(source="admin_user.email", read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = [
            "id", "admin_email", "action", "model_name", "object_id",
            "description", "changes_json", "ip_address", "created_at",
        ]
        read_only_fields = fields


# ── System Settings ────────────────────────────────────────────────────────────

class AdminSystemSettingSerializer(serializers.ModelSerializer):
    updated_by_email = serializers.CharField(source="updated_by.email", read_only=True, default=None)

    class Meta:
        model = SystemSetting
        fields = [
            "key", "value", "value_type", "description",
            "category", "is_editable", "updated_at", "updated_by_email",
        ]
        read_only_fields = ["key", "value_type", "description", "category", "is_editable", "updated_at", "updated_by_email"]

