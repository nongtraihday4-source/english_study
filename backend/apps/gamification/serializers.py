"""
apps/gamification/serializers.py
"""
from rest_framework import serializers

from utils.formatters import fmt_vn
from .models import Achievement, UserAchievement, XPLog, LeaderboardSnapshot, Certificate


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = [
            "id", "name", "name_vi", "description", "category",
            "condition_type", "threshold_value", "icon_url", "icon_emoji",
            "xp_reward",
        ]


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ["id", "achievement", "earned_at"]


class XPLogSerializer(serializers.ModelSerializer):
    xp_amount_display = serializers.SerializerMethodField()

    class Meta:
        model = XPLog
        fields = ["id", "source", "xp_amount", "xp_amount_display", "note", "created_at"]

    def get_xp_amount_display(self, obj):
        return f"+{fmt_vn(obj.xp_amount)} XP"


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    xp_display = serializers.SerializerMethodField()
    is_self = serializers.SerializerMethodField()

    class Meta:
        model = LeaderboardSnapshot
        fields = ["rank", "user", "user_name", "xp_total", "xp_display", "is_self"]

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email.split("@")[0]

    def get_xp_display(self, obj):
        return f"{fmt_vn(obj.xp_total)} XP"

    def get_is_self(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.user_id == request.user.pk
        return False


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    level_name = serializers.CharField(source="level.name", read_only=True)

    class Meta:
        model = Certificate
        fields = [
            "id", "verification_code", "issued_at", "pdf_s3_key",
            "course_title", "level_name",
        ]
