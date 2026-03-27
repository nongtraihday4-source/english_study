"""
App: notifications
Models: Notification, NotificationTemplate
"""
from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ("streak_reminder", "Nhắc nhở streak"),
        ("flashcard_due", "Ôn flashcard đến hạn"),
        ("grading_done", "Chấm bài xong"),
        ("new_lesson", "Bài học mới"),
        ("achievement", "Nhận huy hiệu"),
        ("daily_challenge", "Daily Challenge mới"),
        ("payment_success", "Thanh toán thành công"),
        ("payment_failed", "Thanh toán thất bại"),
        ("subscription_expiring", "Gói chuẩn bị hết hạn"),
        ("system", "Thông báo hệ thống"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications", db_index=True)
    notification_type = models.CharField(max_length=25, choices=TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    reference_id = models.BigIntegerField(null=True, blank=True)
    reference_type = models.CharField(max_length=30, null=True, blank=True)
    action_url = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notifications_notification"
        indexes = [
            models.Index(fields=["user", "is_read", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notify({self.user_id}) {self.notification_type}: {self.title[:40]}"


class NotificationTemplate(models.Model):
    """Reusable templates for bulk/triggered notifications."""
    notification_type = models.CharField(max_length=25, choices=Notification.TYPE_CHOICES, unique=True)
    title_vi = models.CharField(max_length=200)
    message_template_vi = models.TextField(help_text="Sử dụng {{var}} cho biến động")
    push_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notifications_template"
