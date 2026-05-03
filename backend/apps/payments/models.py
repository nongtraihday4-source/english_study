"""
App: payments
Models: SubscriptionPlan, UserSubscription, Coupon, CouponRedemption, PaymentTransaction
"""
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class SubscriptionPlan(models.Model):
    BILLING_CHOICES = [
        ("free", "Demo miễn phí"),
        ("monthly", "Hàng tháng"),
        ("yearly", "Hàng năm"),
        ("lifetime", "Vĩnh viễn"),
    ]

    name = models.CharField(max_length=50, unique=True)
    name_vi = models.CharField(max_length=50)
    billing_period = models.CharField(max_length=10, choices=BILLING_CHOICES)
    price_vnd = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    price_usd = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    original_price_vnd = models.DecimalField(max_digits=12, decimal_places=0, default=0, help_text="Giá gốc (để hiện discount)")
    features_json = models.JSONField(default=list, help_text="Danh sách tính năng dạng list[str]")
    max_lessons_per_day = models.IntegerField(null=True, blank=True, help_text="Null = không giới hạn")
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments_subscriptionplan"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.name_vi} — {int(self.price_vnd):,} VNĐ"


class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ("trial", "Dùng thử"),
        ("active", "Đang hoạt động"),
        ("expired", "Hết hạn"),
        ("cancelled", "Đã huỷ"),
        ("paused", "Tạm dừng"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="trial", db_index=True)
    started_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments_usersubscription"

    @property
    def is_premium(self):
        from django.utils import timezone
        return self.status == "active" and (
            self.expires_at is None or self.expires_at > timezone.now()
        )


class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ("percent", "% giảm giá"),
        ("fixed_vnd", "Giảm số tiền cố định VNĐ"),
    ]

    code = models.CharField(max_length=30, unique=True, db_index=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    max_uses = models.IntegerField(null=True, blank=True, help_text="Null = không giới hạn")
    used_count = models.IntegerField(default=0)
    plan_restriction = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True, help_text="Null = áp dụng tất cả gói")
    valid_from = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    min_purchase_vnd = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments_coupon"

    @property
    def is_available(self):
        from django.utils import timezone
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True

    def __str__(self):
        return f"Coupon:{self.code} ({self.discount_value}{'%' if self.discount_type == 'percent' else 'đ'})"


class CouponRedemption(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name="redemptions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction = models.ForeignKey("PaymentTransaction", on_delete=models.CASCADE, null=True, blank=True)
    discount_applied_vnd = models.DecimalField(max_digits=12, decimal_places=0)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments_couponredemption"
        constraints = [
            models.UniqueConstraint(
                fields=["coupon", "user"],
                name="unique_coupon_per_user",
            )
        ]


class PaymentTransaction(models.Model):
    GATEWAY_CHOICES = [("vnpay", "VNPay"), ("stripe", "Stripe"), ("manual", "Thủ công")]
    STATUS_CHOICES = [
        ("pending", "Chờ thanh toán"),
        ("success", "Thành công"),
        ("failed", "Thất bại"),
        ("cancelled", "Đã huỷ"),
        ("refunded", "Đã hoàn tiền"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="transactions")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    gateway = models.CharField(max_length=10, choices=GATEWAY_CHOICES)
    amount_vnd = models.DecimalField(max_digits=12, decimal_places=0)
    original_amount_vnd = models.DecimalField(max_digits=12, decimal_places=0, help_text="Trước giảm giá")
    discount_vnd = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending", db_index=True)
    gateway_txn_id = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    gateway_response_json = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    webhook_received_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments_paymenttransaction"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["status", "gateway"]),
        ]
