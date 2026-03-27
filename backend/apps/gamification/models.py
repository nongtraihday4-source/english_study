"""
App: gamification
Models: Achievement, UserAchievement, XPLog, LeaderboardSnapshot, Certificate
"""
from django.conf import settings
from django.db import models


class Achievement(models.Model):
    CATEGORY_CHOICES = [
        ("streak", "Streak"),
        ("skill", "Kỹ năng"),
        ("speed", "Tốc độ"),
        ("milestone", "Milestone"),
        ("social", "Social"),
    ]
    CONDITION_TYPES = [
        ("streak_days", "Streak liên tiếp X ngày"),
        ("skill_score_gte", "Điểm kỹ năng ≥ X"),
        ("chapter_in_hours", "Hoàn thành chương trong X giờ"),
        ("night_sessions", "Học sau 22:00 VN X ngày"),
        ("words_learned", "Học được X từ mới"),
        ("lessons_done", "Hoàn thành X bài học"),
        ("perfect_score", "Đạt 100 điểm lần đầu"),
        ("top_leaderboard", "Vào Top X bảng xếp hạng"),
        ("custom", "Điều kiện tùy chỉnh"),
    ]

    name = models.CharField(max_length=100)
    name_vi = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, db_index=True)
    condition_type = models.CharField(max_length=30, choices=CONDITION_TYPES)
    threshold_value = models.IntegerField(default=1)
    icon_url = models.CharField(max_length=500, null=True, blank=True)
    icon_emoji = models.CharField(max_length=10, null=True, blank=True)
    xp_reward = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "gamification_achievement"
        ordering = ["category", "xp_reward"]

    def __str__(self):
        return f"Badge: {self.name_vi} (+{self.xp_reward} XP)"


class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        db_table = "gamification_userachievement"
        constraints = [
            models.UniqueConstraint(fields=["user", "achievement"], name="unique_user_achievement")
        ]


class XPLog(models.Model):
    """Immutable XP event log — source of truth for all XP calculations."""
    SOURCE_CHOICES = [
        ("exercise_complete", "+10 XP — Hoàn thành bài tập"),
        ("perfect_score", "+25 XP — Điểm tuyệt đối 100"),
        ("streak_7", "+50 XP — Streak 7 ngày"),
        ("chapter_complete", "+100 XP — Hoàn thành chương"),
        ("daily_challenge", "+20 XP — Daily Challenge"),
        ("badge_earned", "XP từ huy hiệu"),
        ("admin_grant", "Admin cấp thủ công"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="xp_logs")
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, db_index=True)
    xp_amount = models.IntegerField()
    reference_id = models.BigIntegerField(null=True, blank=True)
    reference_type = models.CharField(max_length=30, null=True, blank=True)
    note = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "gamification_xplog"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["source"]),
        ]

    def __str__(self):
        return f"XP({self.user_id}) +{self.xp_amount} [{self.source}]"


class LeaderboardSnapshot(models.Model):
    """Weekly/Monthly materialised leaderboard — updated by Celery beat."""
    PERIOD_CHOICES = [("weekly", "Tuần"), ("monthly", "Tháng"), ("all_time", "Toàn thời gian")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, db_index=True)
    period_start = models.DateField(db_index=True)
    rank = models.IntegerField()
    xp_total = models.IntegerField(default=0)
    snapshot_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "gamification_leaderboardsnapshot"
        indexes = [
            models.Index(fields=["period", "period_start", "rank"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "period", "period_start"],
                name="unique_user_period_snapshot",
            )
        ]


class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certificates")
    course = models.ForeignKey("curriculum.Course", on_delete=models.CASCADE, null=True, blank=True)
    level = models.ForeignKey("curriculum.CEFRLevel", on_delete=models.CASCADE, null=True, blank=True)
    verification_code = models.CharField(max_length=32, unique=True, db_index=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_s3_key = models.CharField(max_length=500, null=True, blank=True)
    is_valid = models.BooleanField(default=True)

    class Meta:
        db_table = "gamification_certificate"
