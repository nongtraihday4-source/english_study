"""
App: support
Models: SupportTicket, TicketMessage, RefundRequest
"""
from django.db import models
from django.utils import timezone


def _sla_deadline(priority: str):
    """SLA deadline measured in business hours (T2-T7 08:00-17:00, holidays excluded)."""
    from utils.business_hours import business_sla_deadline  # lazy import avoids circular
    return business_sla_deadline(priority)


class SupportTicket(models.Model):
    CATEGORY_CHOICES = [
        ("account", "Tài khoản"),
        ("payment", "Thanh toán"),
        ("technical", "Kỹ thuật"),
        ("content", "Nội dung"),
        ("other", "Khác"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Thấp"),
        ("medium", "Trung bình"),
        ("high", "Cao"),
        ("urgent", "Khẩn"),
    ]
    STATUS_CHOICES = [
        ("open", "Mở"),
        ("in_progress", "Đang xử lý"),
        ("waiting_customer", "Chờ khách hàng"),
        ("resolved", "Đã giải quyết"),
        ("closed", "Đóng"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="support_tickets",
        help_text="Khách hàng liên quan đến ticket",
    )
    assigned_to = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
        help_text="Nhân viên hỗ trợ được giao",
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other", db_index=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium", db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open", db_index=True)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sla_deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tickets",
        help_text="Staff tạo ticket",
    )
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "support_ticket"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["assigned_to", "status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.sla_deadline:
            self.sla_deadline = _sla_deadline(self.priority)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.pk} {self.subject} [{self.status}]"


class TicketMessage(models.Model):
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="ticket_messages",
    )
    content = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Ghi chú nội bộ - không hiển thị với khách hàng",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "support_ticket_message"
        ordering = ["created_at"]

    def __str__(self):
        return f"Message on #{self.ticket_id} by {self.author_id}"


class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Chờ duyệt"),
        ("approved", "Đã duyệt"),
        ("rejected", "Từ chối"),
        ("completed", "Hoàn thành"),
    ]

    transaction = models.ForeignKey(
        "payments.PaymentTransaction",
        on_delete=models.PROTECT,
        related_name="refund_requests",
    )
    requested_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="refund_requests_created",
        help_text="Nhân viên hỗ trợ tạo yêu cầu",
    )
    reason = models.TextField()
    amount_vnd = models.PositiveIntegerField(help_text="Số tiền hoàn (VND)")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending", db_index=True)
    reviewed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refund_requests_reviewed",
        help_text="Admin duyệt/từ chối",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Ghi chú của admin")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "support_refund_request"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Refund #{self.pk} — {self.amount_vnd}VND [{self.status}]"


class PublicSupportRequest(models.Model):
    """
    Requests submitted from public support form (including unauthenticated users).
    Support staff can triage and convert them into normal support tickets.
    """

    ISSUE_TYPE_CHOICES = [
        ("account_access", "Không đăng nhập được / quên thông tin tài khoản"),
        ("payment", "Thanh toán / hoàn tiền"),
        ("technical", "Lỗi kỹ thuật"),
        ("learning", "Vấn đề học tập / nội dung"),
        ("other", "Khác"),
    ]
    STATUS_CHOICES = [
        ("new", "Mới"),
        ("auto_converted", "Đã tự chuyển ticket"),
        ("triaged", "Đã xử lý phân luồng"),
        ("closed", "Đã đóng"),
        ("spam_rejected", "Bị từ chối (spam)"),
    ]

    linked_user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="public_support_requests",
    )
    linked_ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="public_source_requests",
    )
    triaged_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triaged_public_support_requests",
    )

    full_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, default="", db_index=True)
    phone = models.CharField(max_length=20, blank=True, default="", db_index=True)
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPE_CHOICES, db_index=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", db_index=True)
    source = models.CharField(max_length=20, default="public_form")
    is_authenticated_submission = models.BooleanField(default=False)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default="")
    meta = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "support_public_request"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["issue_type", "created_at"]),
        ]

    def __str__(self):
        return f"PublicRequest #{self.pk} [{self.status}] {self.subject}"
