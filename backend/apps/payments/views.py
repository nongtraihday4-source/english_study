"""
apps/payments/views.py
─────────────────────────────────────────────────────────────────────────────
GET  /api/payments/plans/          → List active subscription plans
POST /api/payments/checkout/       → Initiate payment (VNPay / Stripe)
POST /api/payments/coupons/validate/ → Validate coupon code
POST /api/payments/webhooks/vnpay/ → VNPay IPN webhook (unauthenticated)
POST /api/payments/webhooks/stripe/ → Stripe webhook (unauthenticated)
GET  /api/payments/transactions/   → User's own payment history
─────────────────────────────────────────────────────────────────────────────
"""
import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.formatters import fmt_vnd
from .models import Coupon, PaymentTransaction, SubscriptionPlan, UserSubscription
from .serializers import (
    CheckoutSerializer,
    CouponValidateResponseSerializer,
    CouponValidateSerializer,
    PaymentTransactionSerializer,
    SubscriptionPlanSerializer,
)

payment_logger = logging.getLogger("es.payments")


class PlanListView(generics.ListAPIView):
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return SubscriptionPlan.objects.filter(is_active=True).order_by("sort_order")


class CouponValidateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            coupon = Coupon.objects.get(code__iexact=data["code"])
        except Coupon.DoesNotExist:
            return Response({"detail": "Mã coupon không tồn tại."}, status=404)

        if not coupon.is_available:
            return Response({"detail": "Mã coupon đã hết hạn hoặc hết lượt sử dụng."}, status=400)

        already_used = coupon.redemptions.filter(user=request.user).exists()
        if already_used:
            return Response({"detail": "Bạn đã sử dụng mã coupon này rồi."}, status=400)

        try:
            plan = SubscriptionPlan.objects.get(pk=data["plan_id"])
        except SubscriptionPlan.DoesNotExist:
            return Response({"detail": "Gói không tồn tại."}, status=404)

        if coupon.plan_restriction and coupon.plan_restriction != plan:
            return Response({"detail": "Mã coupon này không áp dụng cho gói đã chọn."}, status=400)

        response_data = CouponValidateResponseSerializer(coupon, context={"plan": plan}).data
        return Response(response_data)


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            plan = SubscriptionPlan.objects.get(pk=data["plan_id"], is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({"detail": "Gói không tồn tại."}, status=404)

        original_price = int(plan.price_vnd)
        discount_vnd = 0
        coupon = None

        if data.get("coupon_code"):
            try:
                coupon = Coupon.objects.get(code__iexact=data["coupon_code"])
                if coupon.is_available:
                    if coupon.discount_type == "percent":
                        discount_vnd = int(original_price * float(coupon.discount_value) / 100)
                    else:
                        discount_vnd = min(int(coupon.discount_value), original_price)
            except Coupon.DoesNotExist:
                pass

        final_price = max(0, original_price - discount_vnd)

        txn = PaymentTransaction.objects.create(
            user=request.user,
            plan=plan,
            gateway=data["gateway"],
            amount_vnd=final_price,
            original_amount_vnd=original_price,
            discount_vnd=discount_vnd,
            ip_address=request.META.get("REMOTE_ADDR", "")[:45],
        )

        payment_logger.info(
            "Checkout initiated | user=%s plan=%s gateway=%s amount=%s txn=%s",
            request.user.pk, plan.name, data["gateway"], fmt_vnd(final_price), txn.pk,
        )

        if settings.DEBUG:
            # Simulate real payment in dev environment
            txn.status = "success"
            txn.save()
            _activate_subscription(txn)
            # Detect frontend origin dynamically (works on any port)
            origin = request.META.get("HTTP_ORIGIN") or request.META.get("HTTP_REFERER", "")
            if origin:
                # Strip path from referer, keep scheme+host+port
                from urllib.parse import urlparse
                parsed = urlparse(origin)
                base = f"{parsed.scheme}://{parsed.netloc}"
            else:
                base = "http://localhost:5173"
            payment_url = f"{base}/payment/success?txn={txn.pk}"
        else:
            # TODO: integrate real VNPay/Stripe SDK to get payment_url
            payment_url = f"https://payment-gateway.example.com/pay?txn={txn.pk}&amount={final_price}"

        return Response({
            "transaction_id": txn.pk,
            "amount_vnd": final_price,
            "amount_display": fmt_vnd(final_price),
            "discount_vnd": discount_vnd,
            "payment_url": payment_url,
        }, status=201)


class VNPayWebhookView(APIView):
    """VNPay IPN endpoint — must be publicly accessible, CSRF exempt."""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @csrf_exempt
    def post(self, request):
        params = request.data
        txn_ref = params.get("vnp_TxnRef")
        response_code = params.get("vnp_ResponseCode")
        amount = params.get("vnp_Amount")

        payment_logger.info(
            "VNPay IPN received | txn_ref=%s response_code=%s amount=%s",
            txn_ref, response_code, amount,
        )

        try:
            txn = PaymentTransaction.objects.get(pk=txn_ref, gateway="vnpay")
        except PaymentTransaction.DoesNotExist:
            payment_logger.warning("VNPay IPN: transaction %s not found", txn_ref)
            return Response({"RspCode": "01", "Message": "Order Not Found"})

        if txn.status != "pending":
            return Response({"RspCode": "02", "Message": "Order Already Confirmed"})

        if response_code == "00":
            txn.status = "success"
            txn.webhook_received_at = timezone.now()
            txn.gateway_response_json = dict(params)
            txn.save()
            _activate_subscription(txn)
            payment_logger.info("VNPay payment SUCCESS | txn=%s user=%s", txn.pk, txn.user_id)
        else:
            txn.status = "failed"
            txn.save(update_fields=["status"])

        return Response({"RspCode": "00", "Message": "Confirm Success"})


class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @csrf_exempt
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        stripe_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")

        if stripe_secret:
            expected_sig = hmac.new(
                stripe_secret.encode(), payload, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(f"sha256={expected_sig}", sig_header.split(",")[1] if "," in sig_header else ""):
                payment_logger.warning("Stripe webhook: invalid signature")
                return Response({"detail": "Invalid signature"}, status=400)

        try:
            event = json.loads(payload)
        except Exception:
            return Response({"detail": "Invalid payload"}, status=400)

        event_type = event.get("type")
        payment_logger.info("Stripe webhook | type=%s", event_type)

        if event_type == "payment_intent.succeeded":
            pi = event["data"]["object"]
            txn_id = pi.get("metadata", {}).get("txn_id")
            if txn_id:
                try:
                    txn = PaymentTransaction.objects.get(pk=txn_id, gateway="stripe")
                    txn.status = "success"
                    txn.gateway_txn_id = pi.get("id")
                    txn.webhook_received_at = timezone.now()
                    txn.save()
                    _activate_subscription(txn)
                except PaymentTransaction.DoesNotExist:
                    pass

        return Response({"received": True})


class TransactionListView(generics.ListAPIView):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentTransaction.objects.filter(user=self.request.user).order_by("-created_at")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _activate_subscription(txn: PaymentTransaction) -> None:
    """Called on successful payment — activates or extends subscription."""
    from datetime import timedelta

    plan = txn.plan
    now = timezone.now()

    sub, created = UserSubscription.objects.get_or_create(
        user=txn.user,
        defaults={"plan": plan, "started_at": now, "status": "active"},
    )

    if plan.billing_period == "monthly":
        delta = timedelta(days=30)
    elif plan.billing_period == "yearly":
        delta = timedelta(days=365)
    else:
        delta = timedelta(days=36500)  # lifetime

    start = now if created else (sub.expires_at or now)
    sub.plan = plan
    sub.status = "active"
    sub.expires_at = start + delta
    sub.save()

    # Update user account_type
    txn.user.account_type = "premium"
    txn.user.save(update_fields=["account_type"])

    payment_logger.info(
        "Subscription activated | user=%s plan=%s expires=%s",
        txn.user_id, plan.name, sub.expires_at,
    )
