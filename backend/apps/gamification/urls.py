"""apps/gamification/urls.py"""
from django.urls import path

from .views import (
    AchievementListView,
    CertificateListView,
    LeaderboardView,
    UserAchievementListView,
    XPLogView,
)

urlpatterns = [
    path("achievements/", AchievementListView.as_view(), name="achievement-list"),
    path("my-achievements/", UserAchievementListView.as_view(), name="my-achievements"),
    path("xp-log/", XPLogView.as_view(), name="xp-log"),
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path("certificates/", CertificateListView.as_view(), name="certificate-list"),
]
