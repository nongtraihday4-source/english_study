"""
Serializers for the Support Portal.
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import serializers

from apps.payments.models import Coupon, PaymentTransaction, UserSubscription
from apps.support.models import PublicSupportRequest, RefundRequest, SupportTicket, TicketMessage

User = get_user_model()


# ─── User lookup ─────────────────────────────────────────────────────────────

class SupportUserSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = UserSubscription
        fields = ["id", "plan_name", "status", "expires_at", "updated_at"]


class SupportUserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    phone = serializers.CharField(source="profile.phone", default=None, read_only=True)
    subscription_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "phone",
            "role", "account_type", "current_level",
            "date_joined", "last_login", "is_active",
            "subscription_status",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email

    def get_subscription_status(self, obj):
        sub = getattr(obj, "subscription", None)
        if sub:
            return sub.status
        return None


class SupportUserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    phone = serializers.CharField(source="profile.phone", default=None, read_only=True)
    subscription = SupportUserSubscriptionSerializer(read_only=True)
    recent_transactions = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "phone",
            "role", "account_type", "current_level", "target_level",
            "date_joined", "last_login", "is_active",
            "subscription", "recent_transactions", "ticket_count",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email

    def get_recent_transactions(self, obj):
        txns = obj.transactions.select_related("plan").order_by("-created_at")[:5]
        return [
            {
                "id": t.id,
                "plan": t.plan.name,
                "amount_vnd": int(t.amount_vnd),
                "status": t.status,
                "gateway": t.gateway,
                "created_at": t.created_at.isoformat(),
            }
            for t in txns
        ]

    def get_ticket_count(self, obj):
        return obj.support_tickets.filter(is_deleted=False).count()


# ─── Tickets ─────────────────────────────────────────────────────────────────

class TicketMessageSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_role = serializers.CharField(source="author.role", read_only=True)

    class Meta:
        model = TicketMessage
        fields = ["id", "author_name", "author_role", "content", "is_internal", "created_at"]
        read_only_fields = ["id", "author_name", "author_role", "created_at"]

    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.email
        return "Unknown"


class SupportTicketListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    message_count = serializers.IntegerField(source="messages.count", read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = SupportTicket
        fields = [
            "id", "subject", "category", "priority", "status",
            "user_email", "assigned_to_name", "message_count",
            "sla_deadline", "is_overdue", "created_at", "updated_at",
        ]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.email
        return None

    def get_is_overdue(self, obj):
        from django.utils import timezone
        if obj.sla_deadline and obj.status not in ("resolved", "closed"):
            return timezone.now() > obj.sla_deadline
        return False


class SupportTicketDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    messages = TicketMessageSerializer(many=True, read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = SupportTicket
        fields = [
            "id", "subject", "description", "category", "priority", "status",
            "user_id", "user_email", "assigned_to", "assigned_to_name",
            "sla_deadline", "is_overdue",
            "created_at", "updated_at", "resolved_at",
            "messages",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user_id", "user_email"]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.email
        return None

    def get_is_overdue(self, obj):
        from django.utils import timezone
        if obj.sla_deadline and obj.status not in ("resolved", "closed"):
            return timezone.now() > obj.sla_deadline
        return False


class SupportTicketCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    sla_deadline = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SupportTicket
        fields = [
            "id",
            "subject",
            "description",
            "category",
            "priority",
            "user",
            "status",
            "sla_deadline",
        ]


# ─── Payments (read-only views) ───────────────────────────────────────────────

class SupportTransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            "id", "user_email", "plan_name",
            "gateway", "amount_vnd", "original_amount_vnd", "discount_vnd",
            "status", "gateway_txn_id", "created_at",
        ]


class SupportSubscriptionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = UserSubscription
        fields = ["id", "user_email", "plan_name", "status", "expires_at", "updated_at"]


class SupportCouponSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coupon
        fields = [
            "id", "code", "discount_type", "discount_value",
            "used_count", "max_uses", "valid_from", "expires_at",
            "is_active", "is_available", "min_purchase_vnd",
        ]


# ─── Refund Requests ─────────────────────────────────────────────────────────

class RefundRequestSerializer(serializers.ModelSerializer):
    transaction_id = serializers.IntegerField(source="transaction.id", read_only=True)
    user_email = serializers.SerializerMethodField()
    requested_by_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RefundRequest
        fields = [
            "id", "transaction_id", "user_email",
            "reason", "amount_vnd", "status",
            "requested_by_name", "reviewed_by_name", "reviewed_at", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "status", "reviewed_by_name", "reviewed_at", "notes", "created_at", "updated_at"]

    def get_user_email(self, obj):
        return obj.transaction.user.email if obj.transaction and obj.transaction.user else None

    def get_requested_by_name(self, obj):
        if obj.requested_by:
            return f"{obj.requested_by.first_name} {obj.requested_by.last_name}".strip() or obj.requested_by.email
        return None

    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return f"{obj.reviewed_by.first_name} {obj.reviewed_by.last_name}".strip() or obj.reviewed_by.email
        return None


class RefundRequestCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = RefundRequest
        fields = ["id", "transaction", "reason", "amount_vnd", "status", "created_at"]

    def validate_amount_vnd(self, value):
        if value <= 0:
            raise serializers.ValidationError("Số tiền hoàn phải lớn hơn 0.")
        return value

    def validate(self, data):
        txn = data.get("transaction")
        if txn and txn.status not in ("success",):
            raise serializers.ValidationError(
                {"transaction": "Chỉ có thể hoàn tiền cho giao dịch thành công."}
            )
        if txn and int(data.get("amount_vnd", 0)) > int(txn.amount_vnd):
            raise serializers.ValidationError(
                {"amount_vnd": "Số tiền hoàn không được vượt quá giá trị giao dịch."}
            )
        if txn and RefundRequest.objects.filter(transaction=txn, status__in=("pending", "approved")).exists():
            raise serializers.ValidationError(
                {"transaction": "Giao dịch này đã có yêu cầu hoàn tiền đang chờ xử lý."}
            )
        return data


# ─── Dashboard ───────────────────────────────────────────────────────────────

class SupportDashboardSerializer(serializers.Serializer):
    open_tickets = serializers.IntegerField()
    my_tickets = serializers.IntegerField()
    pending_refunds = serializers.IntegerField()
    resolved_today = serializers.IntegerField()
    overdue_tickets = serializers.IntegerField()


# ─── Public Support Requests ────────────────────────────────────────────────

class PublicSupportRequestCreateSerializer(serializers.ModelSerializer):
    consent = serializers.BooleanField(write_only=True)
    honeypot = serializers.CharField(write_only=True, required=False, allow_blank=True, default="")

    class Meta:
        model = PublicSupportRequest
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "issue_type",
            "subject",
            "description",
            "consent",
            "honeypot",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_full_name(self, value):
        text = (value or "").strip()
        if len(text) < 2:
            raise serializers.ValidationError("Vui lòng nhập họ tên hợp lệ.")
        return text

    def validate_subject(self, value):
        text = (value or "").strip()
        if len(text) < 8:
            raise serializers.ValidationError("Tiêu đề cần ít nhất 8 ký tự.")
        return text

    def validate_description(self, value):
        text = (value or "").strip()
        if len(text) < 30:
            raise serializers.ValidationError("Mô tả cần chi tiết tối thiểu 30 ký tự.")
        return text

    def validate_phone(self, value):
        raw = (value or "").strip()
        digits = "".join(ch for ch in raw if ch.isdigit())
        if raw and len(digits) < 9:
            raise serializers.ValidationError("Số điện thoại không hợp lệ.")
        return raw

    def validate(self, attrs):
        request = self.context.get("request")
        email = (attrs.get("email") or "").strip()
        phone = (attrs.get("phone") or "").strip()
        issue_type = attrs.get("issue_type")

        if attrs.get("honeypot"):
            raise serializers.ValidationError({"detail": "Yêu cầu không hợp lệ."})
        attrs.pop("honeypot", None)

        if not attrs.get("consent"):
            raise serializers.ValidationError({"consent": "Bạn cần xác nhận thông tin là chính xác."})
        attrs.pop("consent", None)

        if not email and not phone:
            raise serializers.ValidationError({"detail": "Vui lòng cung cấp email hoặc số điện thoại để liên hệ."})

        if request and not request.user.is_authenticated:
            allowed = {"account_access", "payment", "technical", "other"}
            if issue_type not in allowed:
                raise serializers.ValidationError({
                    "issue_type": "Khi chưa đăng nhập, bạn chỉ có thể gửi yêu cầu tài khoản, thanh toán hoặc kỹ thuật.",
                })

        dedupe_qs = PublicSupportRequest.objects.filter(
            created_at__gte=timezone.now() - timedelta(minutes=30),
            issue_type=issue_type,
            subject__iexact=attrs.get("subject", ""),
        )
        if email:
            dedupe_qs = dedupe_qs.filter(email__iexact=email)
        elif phone:
            dedupe_qs = dedupe_qs.filter(phone=phone)
        if dedupe_qs.exists():
            raise serializers.ValidationError({
                "detail": "Bạn vừa gửi yêu cầu tương tự. Vui lòng chờ nhân viên phản hồi trước khi gửi lại.",
            })

        attrs["email"] = email
        attrs["phone"] = phone
        attrs["subject"] = (attrs.get("subject") or "").strip()
        attrs["description"] = (attrs.get("description") or "").strip()
        return attrs


class PublicSupportRequestListSerializer(serializers.ModelSerializer):
    linked_ticket_id = serializers.IntegerField(source="linked_ticket.id", read_only=True)
    linked_user_id = serializers.IntegerField(source="linked_user.id", read_only=True)
    linked_user_email = serializers.EmailField(source="linked_user.email", read_only=True)
    triaged_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PublicSupportRequest
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "issue_type",
            "subject",
            "description",
            "status",
            "linked_ticket_id",
            "linked_user_id",
            "linked_user_email",
            "triaged_by_name",
            "is_authenticated_submission",
            "created_at",
            "updated_at",
        ]

    def get_triaged_by_name(self, obj):
        if not obj.triaged_by:
            return None
        return f"{obj.triaged_by.first_name} {obj.triaged_by.last_name}".strip() or obj.triaged_by.email
