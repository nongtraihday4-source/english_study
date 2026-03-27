"""
App: users
Models: User, UserProfile, UserSettings, SessionToken
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model.
    email is the login field; username kept for display only.
    """
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("teacher", "Giáo viên"),
        ("student", "Học viên"),
    ]
    ACCOUNT_CHOICES = [
        ("demo", "Demo"),
        ("premium", "Premium"),
    ]
    CEFR_CHOICES = [
        ("A1", "A1"), ("A2", "A2"),
        ("B1", "B1"), ("B2", "B2"),
        ("C1", "C1"), ("C2", "C2"),
    ]

    # Override email to be unique and required
    email = models.EmailField(max_length=150, unique=True, db_index=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student", db_index=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_CHOICES, default="demo")
    current_level = models.CharField(max_length=3, choices=CEFR_CHOICES, default="A1")
    target_level = models.CharField(max_length=3, choices=CEFR_CHOICES, default="B2")
    is_deleted = models.BooleanField(default=False, db_index=True)  # Soft-delete

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users_user"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role", "is_deleted"]),
        ]

    def __str__(self):
        return f"{self.email} ({self.role})"


class UserProfile(models.Model):
    GENDER_CHOICES = [("male", "Nam"), ("female", "Nữ"), ("other", "Khác")]
    ACCENT_CHOICES = [("uk", "British"), ("us", "American")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    native_language = models.CharField(max_length=5, default="vi")
    preferred_accent = models.CharField(max_length=5, choices=ACCENT_CHOICES, default="uk")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_userprofile"

    def __str__(self):
        return f"Profile({self.user.email})"


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    dark_mode = models.BooleanField(default=False)
    daily_goal_minutes = models.IntegerField(default=20)
    reminder_time = models.TimeField(null=True, blank=True)
    notify_streak = models.BooleanField(default=True)
    notify_flashcard_due = models.BooleanField(default=True)
    notify_new_lesson = models.BooleanField(default=True)
    # Hour (0-23) in ICT (UTC+7) when the daily flashcard reminder fires.
    # Default 8 = 08:00 ICT = 01:00 UTC.
    flashcard_notify_hour = models.SmallIntegerField(
        default=8,
        help_text="Giờ nhắc nhở flashcard (0-23, múi giờ ICT UTC+7)",
    )
    language_ui = models.CharField(max_length=5, default="vi")
    
    # 2FA (Two-factor authentication)
    totp_secret = models.CharField(max_length=32, blank=True, null=True, help_text="Bí mật TOTP base32")
    is_2fa_enabled = models.BooleanField(default=False, help_text="Cờ bật tắt bảo mật 2 lớp 2FA")

    class Meta:
        db_table = "users_usersettings"


class SessionToken(models.Model):
    """
    Layer 3: Multi-device JWT session tracking.
    Stores JTI of each issued refresh token to enable per-device revocation.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="session_tokens")
    jti = models.CharField(max_length=64, unique=True, db_index=True)
    device_name = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)

    class Meta:
        db_table = "users_sessiontoken"
        indexes = [
            models.Index(fields=["user", "is_revoked"]),
            models.Index(fields=["jti"]),
        ]

    def __str__(self):
        return f"Session({self.user.email} jti={self.jti[:8]}…)"
