"""
apps/admin_portal/models.py
New models that live in the admin_portal app (add to INSTALLED_APPS + migrate).
"""
from django.conf import settings
from django.db import models


class StaffPermission(models.Model):
    """Per-staff module access control for admin users."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_permissions",
    )
    manage_users = models.BooleanField(default=False)
    manage_content = models.BooleanField(default=False)
    manage_payments = models.BooleanField(default=False)
    manage_assessments = models.BooleanField(default=False)
    manage_notifications = models.BooleanField(default=False)
    manage_gamification = models.BooleanField(default=False)
    view_analytics = models.BooleanField(default=False)
    manage_settings = models.BooleanField(default=False)
    view_audit_log = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="+",
    )

    class Meta:
        db_table = "admin_portal_staffpermission"

    def __str__(self):
        return f"StaffPermission({self.user_id})"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Tạo mới"),
        ("update", "Cập nhật"),
        ("delete", "Xoá"),
        ("ban", "Khoá tài khoản"),
        ("unban", "Mở khoá tài khoản"),
        ("bulk_notify", "Gửi thông báo hàng loạt"),
        ("extend_sub", "Gia hạn gói"),
        ("grant_xp", "Cấp XP thủ công"),
        ("retry_job", "Thử lại AI Job"),
        ("other", "Khác"),
    ]

    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    model_name = models.CharField(max_length=50, db_index=True)
    object_id = models.BigIntegerField(null=True, blank=True)
    description = models.TextField()
    changes_json = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "admin_portal_auditlog"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["admin_user", "created_at"]),
            models.Index(fields=["action", "model_name"]),
        ]

    def __str__(self):
        return f"AuditLog({self.admin_user_id}) {self.action} {self.model_name}:{self.object_id}"


class SystemSetting(models.Model):
    CATEGORY_CHOICES = [
        ("general", "Chung"),
        ("payment", "Thanh toán"),
        ("ai_grading", "AI Chấm bài"),
        ("email", "Email"),
        ("security", "Bảo mật"),
        ("gamification", "Gamification"),
    ]
    VALUE_TYPE_CHOICES = [
        ("str", "Text"),
        ("int", "Số nguyên"),
        ("bool", "Boolean"),
        ("json", "JSON"),
    ]

    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField()
    value_type = models.CharField(max_length=5, choices=VALUE_TYPE_CHOICES, default="str")
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, db_index=True, default="general")
    is_editable = models.BooleanField(default=True, help_text="False = hiển thị để biết, không cho sửa")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="+",
    )

    class Meta:
        db_table = "admin_portal_systemsetting"
        ordering = ["category", "key"]

    def __str__(self):
        return f"Setting:{self.key}={self.value}"

    @classmethod
    def get(cls, key, default=None):
        try:
            s = cls.objects.get(key=key)
            if s.value_type == "bool":
                return s.value.lower() in ("true", "1", "yes")
            if s.value_type == "int":
                return int(s.value)
            if s.value_type == "json":
                import json
                return json.loads(s.value)
            return s.value
        except cls.DoesNotExist:
            return default
