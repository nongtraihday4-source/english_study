"""
Support Portal Views — for users with role='support' or role='admin'.

All views enforce IsSupportStaff permission.
Support staff can:
  - Look up users (email/phone/name) — READ ONLY
  - Send password reset email to a user
  - View payment transactions & subscriptions — READ ONLY
  - View coupons — READ ONLY
  - Manage support tickets (CRUD + messaging + assignment)
  - Create refund requests (admin approves separately)
"""
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.payments.models import Coupon, PaymentTransaction, UserSubscription
from apps.support.models import PublicSupportRequest, RefundRequest, SupportTicket, TicketMessage
from apps.support.serializers import (
    PublicSupportRequestCreateSerializer,
    PublicSupportRequestListSerializer,
    RefundRequestCreateSerializer,
    RefundRequestSerializer,
    SupportCouponSerializer,
    SupportSubscriptionSerializer,
    SupportTicketCreateSerializer,
    SupportTicketDetailSerializer,
    SupportTicketListSerializer,
    SupportTransactionSerializer,
    SupportUserDetailSerializer,
    SupportUserListSerializer,
)
from utils.pagination import StandardPagination
from utils.permissions import IsSupportStaff

User = get_user_model()
logger = logging.getLogger(__name__)


def _ticket_category_from_issue_type(issue_type: str) -> str:
    mapping = {
        "account_access": "account",
        "payment": "payment",
        "technical": "technical",
        "learning": "content",
        "other": "other",
    }
    return mapping.get(issue_type, "other")


def _extract_client_ip(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _find_user_by_contact(email: str, phone: str):
    if email:
        user = User.objects.filter(is_deleted=False, email__iexact=email).first()
        if user:
            return user
    if phone:
        digits = "".join(ch for ch in phone if ch.isdigit())
        if digits:
            return User.objects.filter(
                is_deleted=False,
                profile__phone__iregex=fr"[0-9]*{digits}[0-9]*",
            ).first()
    return None


# ─── Dashboard ────────────────────────────────────────────────────────────────

class SupportDashboardView(APIView):
    permission_classes = [IsSupportStaff]

    def get(self, request):
        try:
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            user = request.user

            open_tickets = SupportTicket.objects.filter(
                status__in=("open", "in_progress", "waiting_customer"),
                is_deleted=False,
            ).count()

            my_tickets = SupportTicket.objects.filter(
                assigned_to=user,
                status__in=("open", "in_progress", "waiting_customer"),
                is_deleted=False,
            ).count()

            pending_refunds = RefundRequest.objects.filter(status="pending").count()

            resolved_today = SupportTicket.objects.filter(
                status__in=("resolved", "closed"),
                resolved_at__gte=today_start,
                is_deleted=False,
            ).count()

            overdue_tickets = SupportTicket.objects.filter(
                status__in=("open", "in_progress", "waiting_customer"),
                sla_deadline__lt=timezone.now(),
                is_deleted=False,
            ).count()

            # Recently updated tickets assigned to me
            my_recent = SupportTicket.objects.filter(
                assigned_to=user,
                is_deleted=False,
            ).order_by("-updated_at")[:5]
            my_recent_data = SupportTicketListSerializer(my_recent, many=True).data

            # All open overdue tickets
            overdue_list = SupportTicket.objects.filter(
                status__in=("open", "in_progress", "waiting_customer"),
                sla_deadline__lt=timezone.now(),
                is_deleted=False,
            ).order_by("sla_deadline")[:5]
            overdue_data = SupportTicketListSerializer(overdue_list, many=True).data

            return Response({
                "stats": {
                    "open_tickets": open_tickets,
                    "my_tickets": my_tickets,
                    "pending_refunds": pending_refunds,
                    "resolved_today": resolved_today,
                    "overdue_tickets": overdue_tickets,
                },
                "my_recent_tickets": my_recent_data,
                "overdue_tickets_list": overdue_data,
            })
        except Exception as exc:
            logger.exception("SupportDashboardView error: %s", exc)
            return Response({"detail": f"Lỗi server: {exc}"}, status=500)


# ─── User Lookup ──────────────────────────────────────────────────────────────

class SupportUserLookupView(generics.ListAPIView):
    """Search users by email, phone number, or name. READ ONLY."""
    serializer_class = SupportUserListSerializer
    permission_classes = [IsSupportStaff]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = User.objects.filter(is_deleted=False).select_related("profile", "subscription").order_by("-date_joined")
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(profile__phone__icontains=search)
            )
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)
        account_type = self.request.query_params.get("account_type")
        if account_type:
            qs = qs.filter(account_type=account_type)
        return qs


class SupportUserDetailView(generics.RetrieveAPIView):
    """Full user details with subscription and payment history. READ ONLY."""
    serializer_class = SupportUserDetailSerializer
    permission_classes = [IsSupportStaff]

    def get_queryset(self):
        return User.objects.filter(is_deleted=False).select_related("profile", "subscription__plan")


# ─── Password Reset ───────────────────────────────────────────────────────────

class SupportPasswordResetView(APIView):
    """
    POST {user_id}: Generate a password reset token and send email to the user.
    Support staff does NOT see or set the password — only triggers the email.
    """
    permission_classes = [IsSupportStaff]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, is_deleted=False)
        try:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            # In production this should be the real frontend URL from settings
            from django.conf import settings
            frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
            reset_url = f"{frontend_url}/reset-password?uid={uid}&token={token}"

            send_mail(
                subject="[English Study] Đặt lại mật khẩu",
                message=(
                    f"Xin chào {user.first_name or user.email},\n\n"
                    f"Nhân viên hỗ trợ đã gửi yêu cầu đặt lại mật khẩu cho tài khoản của bạn.\n\n"
                    f"Nhấn vào link sau để đặt mật khẩu mới (hiệu lực trong 24 giờ):\n{reset_url}\n\n"
                    f"Nếu bạn không yêu cầu, hãy bỏ qua email này.\n\n"
                    f"Trân trọng,\nTeam English Study"
                ),
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@english-study.vn"),
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(
                "Password reset email sent to %s by support staff %s",
                user.email, request.user.email,
            )
            return Response({"detail": f"Đã gửi email đặt lại mật khẩu đến {user.email}."})
        except Exception as exc:
            logger.exception("SupportPasswordResetView error: %s", exc)
            return Response({"detail": f"Không thể gửi email: {exc}"}, status=500)


class PublicSupportRequestCreateView(APIView):
    """
    Public endpoint for users (including non-logged-in users) to submit support requests.
    Backend tries to auto-link user and auto-convert to support ticket when possible.
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "support_public_request"

    def post(self, request):
        serializer = PublicSupportRequestCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data
        req_obj = PublicSupportRequest.objects.create(
            **payload,
            is_authenticated_submission=bool(request.user and request.user.is_authenticated),
            ip_address=_extract_client_ip(request),
            user_agent=(request.META.get("HTTP_USER_AGENT", "") or "")[:255],
            meta={
                "referer": request.META.get("HTTP_REFERER", ""),
            },
        )

        linked_user = None
        if request.user and request.user.is_authenticated:
            linked_user = request.user
        else:
            linked_user = _find_user_by_contact(req_obj.email, req_obj.phone)

        ticket = None
        if linked_user:
            ticket = SupportTicket.objects.create(
                user=linked_user,
                category=_ticket_category_from_issue_type(req_obj.issue_type),
                priority="medium",
                subject=req_obj.subject,
                description=(
                    f"[Public Support Form]\n"
                    f"Người gửi: {req_obj.full_name}\n"
                    f"Email: {req_obj.email or '-'}\n"
                    f"SĐT: {req_obj.phone or '-'}\n"
                    f"\n{req_obj.description}"
                ),
            )
            req_obj.linked_user = linked_user
            req_obj.linked_ticket = ticket
            req_obj.status = "auto_converted"
            req_obj.save(update_fields=["linked_user", "linked_ticket", "status", "updated_at"])

        return Response(
            {
                "request_id": req_obj.id,
                "ticket_id": ticket.id if ticket else None,
                "queued": bool(ticket),
                "detail": (
                    "Yêu cầu đã được tiếp nhận và đưa vào hàng đợi xử lý."
                    if ticket
                    else "Yêu cầu đã được ghi nhận. Nhân viên CSKH sẽ xác minh thông tin và phản hồi sớm."
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class SupportPublicRequestListView(generics.ListAPIView):
    """Support inbox for public requests that need triage."""

    serializer_class = PublicSupportRequestListSerializer
    permission_classes = [IsSupportStaff]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = PublicSupportRequest.objects.select_related("linked_user", "linked_ticket", "triaged_by")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        search = (self.request.query_params.get("search") or "").strip()
        if search:
            qs = qs.filter(
                Q(subject__icontains=search)
                | Q(full_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )
        return qs.order_by("-created_at")


class SupportPublicRequestConvertView(APIView):
    """Convert a triaged public request to normal support ticket."""

    permission_classes = [IsSupportStaff]

    def post(self, request, pk):
        req_obj = get_object_or_404(PublicSupportRequest, pk=pk)
        if req_obj.linked_ticket_id:
            return Response(
                {
                    "detail": "Yêu cầu này đã được chuyển thành ticket.",
                    "ticket_id": req_obj.linked_ticket_id,
                }
            )

        user_id = request.data.get("user_id") or req_obj.linked_user_id
        if not user_id:
            return Response(
                {"detail": "Thiếu user_id để chuyển yêu cầu thành ticket."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        linked_user = get_object_or_404(User, pk=user_id, is_deleted=False)

        ticket = SupportTicket.objects.create(
            user=linked_user,
            category=_ticket_category_from_issue_type(req_obj.issue_type),
            priority="medium",
            subject=req_obj.subject,
            description=(
                f"[Public Support Form - Triaged by {request.user.email}]\n"
                f"Người gửi: {req_obj.full_name}\n"
                f"Email: {req_obj.email or '-'}\n"
                f"SĐT: {req_obj.phone or '-'}\n"
                f"\n{req_obj.description}"
            ),
            created_by=request.user,
            assigned_to=request.user,
            status="in_progress",
        )

        req_obj.linked_user = linked_user
        req_obj.linked_ticket = ticket
        req_obj.triaged_by = request.user
        req_obj.status = "triaged"
        req_obj.save(update_fields=["linked_user", "linked_ticket", "triaged_by", "status", "updated_at"])

        return Response(
            {
                "detail": "Đã chuyển yêu cầu thành ticket xử lý.",
                "ticket_id": ticket.id,
            },
            status=status.HTTP_201_CREATED,
        )


# ─── Tickets ─────────────────────────────────────────────────────────────────

class SupportTicketListView(generics.ListCreateAPIView):
    permission_classes = [IsSupportStaff]
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SupportTicketCreateSerializer
        return SupportTicketListSerializer

    def get_queryset(self):
        qs = SupportTicket.objects.filter(is_deleted=False).select_related(
            "user", "assigned_to"
        ).annotate(message_count=Count("messages"))

        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)

        priority = self.request.query_params.get("priority")
        if priority:
            qs = qs.filter(priority=priority)

        assigned = self.request.query_params.get("assigned_to")
        if assigned == "me":
            qs = qs.filter(assigned_to=self.request.user)
        elif assigned == "unassigned":
            qs = qs.filter(assigned_to__isnull=True)

        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(subject__icontains=search) | Q(user__email__icontains=search)
            )

        return qs.order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SupportTicketDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsSupportStaff]
    serializer_class = SupportTicketDetailSerializer

    def get_queryset(self):
        return SupportTicket.objects.filter(is_deleted=False).select_related(
            "user", "assigned_to"
        ).prefetch_related("messages__author")

    def perform_update(self, serializer):
        old_status = self.get_object().status
        obj = serializer.save()
        # Auto-set resolved_at when ticket is resolved/closed
        if obj.status in ("resolved", "closed") and old_status not in ("resolved", "closed"):
            obj.resolved_at = timezone.now()
            obj.save(update_fields=["resolved_at"])


def _send_ticket_reply_email(ticket: SupportTicket, msg: TicketMessage, staff_user) -> bool:
    """Send customer-facing email when staff posts a public reply."""
    from django.conf import settings as cfg

    try:
        staff_name = f"{getattr(staff_user, 'first_name', '')} {getattr(staff_user, 'last_name', '')}".strip() or getattr(staff_user, "email", "")
        support_url = f"{getattr(cfg, 'FRONTEND_URL', 'http://localhost:5173')}/help/support-request"

        send_mail(
            subject=f"[English Study Hỗ trợ] Phản hồi ticket #{ticket.id} — {ticket.subject}",
            message=(
                f"Xin chào {ticket.user.first_name or ticket.user.email},\n\n"
                f"Nhân viên hỗ trợ {staff_name} vừa phản hồi yêu cầu của bạn:\n\n"
                f"{'─'*50}\n{msg.content}\n{'─'*50}\n\n"
                f"Tiêu đề: {ticket.subject}\n"
                f"Trạng thái: {ticket.get_status_display()}\n\n"
                f"Cần hỗ trợ thêm? {support_url}\n\n"
                f"Trân trọng,\nTeam English Study"
            ),
            from_email=getattr(cfg, "DEFAULT_FROM_EMAIL", "noreply@english-study.vn"),
            recipient_list=[ticket.user.email],
            fail_silently=False,
        )
        logger.info("Reply email → %s (ticket #%s)", ticket.user.email, ticket.id)
        return True
    except Exception as exc:  # pragma: no cover - logging side effect
        logger.warning("Reply email FAILED #%s: %s", ticket.id, exc)
        return False


class SupportTicketMessageView(APIView):
    """POST a new message to an existing ticket."""
    permission_classes = [IsSupportStaff]

    def post(self, request, pk):
        ticket = get_object_or_404(
            SupportTicket.objects.select_related("user"), pk=pk, is_deleted=False
        )
        content = request.data.get("content", "").strip()
        if not content:
            return Response({"detail": "Nội dung không được để trống."}, status=400)
        is_internal = bool(request.data.get("is_internal", False))
        msg = TicketMessage.objects.create(
            ticket=ticket,
            author=request.user,
            content=content,
            is_internal=is_internal,
        )
        # Auto move to in_progress if open
        if ticket.status == "open":
            ticket.status = "in_progress"
            ticket.save(update_fields=["status", "updated_at"])
        email_sent = False
        if (not is_internal) and ticket.user and ticket.user.email:
            email_sent = _send_ticket_reply_email(ticket, msg, request.user)
        author_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email
        return Response({
            "id": msg.id,
            "author_name": author_name,
            "author_role": request.user.role,
            "content": msg.content,
            "is_internal": msg.is_internal,
            "created_at": msg.created_at.isoformat(),
            "email_sent": email_sent,
        }, status=201)


class SupportTicketAssignView(APIView):
    """POST: assign ticket to self or another support staff user."""
    permission_classes = [IsSupportStaff]

    def post(self, request, pk):
        ticket = get_object_or_404(SupportTicket, pk=pk, is_deleted=False)
        assign_to_id = request.data.get("assign_to_id")
        if assign_to_id:
            staff = get_object_or_404(User, pk=assign_to_id, role__in=("support", "admin"))
            ticket.assigned_to = staff
        else:
            # Assign to self
            ticket.assigned_to = request.user
        if ticket.status == "open":
            ticket.status = "in_progress"
        ticket.save(update_fields=["assigned_to", "status", "updated_at"])
        return Response({
            "detail": f"Ticket đã được giao cho {ticket.assigned_to.email}.",
            "assigned_to": ticket.assigned_to.email,
            "status": ticket.status,
        })


# ─── Payments (read-only) ─────────────────────────────────────────────────────

class SupportTransactionListView(generics.ListAPIView):
    serializer_class = SupportTransactionSerializer
    permission_classes = [IsSupportStaff]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = PaymentTransaction.objects.select_related("user", "plan").order_by("-created_at")
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(user__email__icontains=search)
                | Q(gateway_txn_id__icontains=search)
            )
        txn_status = self.request.query_params.get("status")
        if txn_status:
            qs = qs.filter(status=txn_status)
        gateway = self.request.query_params.get("gateway")
        if gateway:
            qs = qs.filter(gateway=gateway)
        return qs


class SupportSubscriptionListView(generics.ListAPIView):
    serializer_class = SupportSubscriptionSerializer
    permission_classes = [IsSupportStaff]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = UserSubscription.objects.select_related("user", "plan").order_by("-updated_at")
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(user__email__icontains=search)
        sub_status = self.request.query_params.get("status")
        if sub_status:
            qs = qs.filter(status=sub_status)
        return qs


class SupportCouponListView(generics.ListAPIView):
    """Read-only list of coupons for support staff to share with customers."""
    serializer_class = SupportCouponSerializer
    permission_classes = [IsSupportStaff]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = Coupon.objects.order_by("-created_at")
        active_only = self.request.query_params.get("active_only", "true").lower() == "true"
        if active_only:
            qs = qs.filter(is_active=True)
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(code__icontains=search)
        return qs


# ─── Refund Requests ──────────────────────────────────────────────────────────

class SupportRefundRequestListView(generics.ListCreateAPIView):
    permission_classes = [IsSupportStaff]
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RefundRequestCreateSerializer
        return RefundRequestSerializer

    def get_queryset(self):
        qs = RefundRequest.objects.select_related(
            "transaction__user", "transaction__plan",
            "requested_by", "reviewed_by"
        ).order_by("-created_at")
        refund_status = self.request.query_params.get("status")
        if refund_status:
            qs = qs.filter(status=refund_status)
        return qs

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)


class SupportRefundRequestDetailView(generics.RetrieveAPIView):
    serializer_class = RefundRequestSerializer
    permission_classes = [IsSupportStaff]

    def get_queryset(self):
        return RefundRequest.objects.select_related(
            "transaction__user", "transaction__plan",
            "requested_by", "reviewed_by"
        )
