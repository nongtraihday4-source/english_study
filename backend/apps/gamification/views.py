"""
apps/gamification/views.py
"""
from rest_framework import generics, permissions

from utils.permissions import IsAdmin
from .models import Achievement, Certificate, LeaderboardSnapshot, UserAchievement, XPLog
from .serializers import (
    AchievementSerializer,
    CertificateSerializer,
    LeaderboardEntrySerializer,
    UserAchievementSerializer,
    XPLogSerializer,
)


class AchievementListView(generics.ListAPIView):
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Achievement.objects.filter(is_active=True).order_by("category", "xp_reward")


class UserAchievementListView(generics.ListAPIView):
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            UserAchievement.objects.filter(user=self.request.user)
            .select_related("achievement")
            .order_by("-earned_at")
        )


class XPLogView(generics.ListAPIView):
    serializer_class = XPLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return XPLog.objects.filter(user=self.request.user).order_by("-created_at")[:50]


class LeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        period = self.request.query_params.get("period", "weekly")
        qs = (
            LeaderboardSnapshot.objects.filter(period=period)
            .select_related("user")
            .order_by("rank")[:100]
        )
        if not qs.exists():
            # Fallback: live XP query (when snapshot not yet computed)
            from apps.gamification.services import build_live_leaderboard
            return build_live_leaderboard(period)
        return qs


class CertificateListView(generics.ListAPIView):
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(user=self.request.user, is_valid=True)
