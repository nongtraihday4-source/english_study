from django.contrib import admin

from .models import Achievement, Certificate, LeaderboardSnapshot, UserAchievement, XPLog


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ["name_vi", "category", "condition_type", "threshold_value", "xp_reward", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "name_vi"]


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ["user", "achievement", "earned_at"]
    search_fields = ["user__email"]


@admin.register(XPLog)
class XPLogAdmin(admin.ModelAdmin):
    list_display = ["user", "source", "xp_amount", "note", "created_at"]
    list_filter = ["source"]
    search_fields = ["user__email"]


@admin.register(LeaderboardSnapshot)
class LeaderboardSnapshotAdmin(admin.ModelAdmin):
    list_display = ["user", "period", "period_start", "rank", "xp_total"]
    list_filter = ["period"]


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ["user", "course", "level", "verification_code", "issued_at", "is_valid"]
    search_fields = ["user__email", "verification_code"]
