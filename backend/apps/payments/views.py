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
import urllib.parse
from datetime import datetime

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
        elif data["gateway"] == "vnpay":
            payment_url = _build_vnpay_url(txn, request)
        elif data["gateway"] == "stripe":
            payment_url = _build_stripe_url(txn)
        else:
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

def _build_vnpay_url(txn: PaymentTransaction, request) -> str:
    """
    Build a VNPay payment URL using HMAC-SHA512 signature.
    Follows VNPay API v2.1 specification.
    https://sandbox.vnpayment.vn/apis/docs/thanh-toan-pay/pay.html
    """
    tmn_code = getattr(settings, "VNPAY_TMN_CODE", "")
    hash_secret = getattr(settings, "VNPAY_HASH_SECRET", "")
    vnpay_url = getattr(settings, "VNPAY_PAYMENT_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
    return_url = getattr(settings, "VNPAY_RETURN_URL", "http://localhost:5173/payment/success")

    if not tmn_code or not hash_secret:
        payment_logger.warning("VNPay not configured (missing TMN_CODE or HASH_SECRET) — returning placeholder URL")
        return f"https://sandbox.vnpayment.vn/pay?txn={txn.pk}&amount={txn.amount_vnd}"

    now = datetime.now()
    from datetime import timedelta as _td
    create_date = now.strftime("%Y%m%d%H%M%S")
    expire_date = (now + _td(minutes=15)).strftime("%Y%m%d%H%M%S")
    ip_address = request.META.get("REMOTE_ADDR", "127.0.0.1")

    # VNPay requires amount * 100 (tính theo đồng, không có lẻ)
    vnp_amount = int(txn.amount_vnd) * 100

    params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": tmn_code,
        "vnp_Amount": str(vnp_amount),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": str(txn.pk),
        "vnp_OrderInfo": f"Thanh toan goi hoc {txn.plan.name}",
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": f"{return_url}?txn={txn.pk}",
        "vnp_IpAddr": ip_address,
        "vnp_CreateDate": create_date,
        "vnp_ExpireDate": expire_date,
    }

    # Sort by key name (required by VNPay spec)
    sorted_params = sorted(params.items())
    hash_data = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params)
    secure_hash = hmac.new(
        hash_secret.encode("utf-8"),
        hash_data.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()

    query_string = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params)
    payment_url = f"{vnpay_url}?{query_string}&vnp_SecureHash={secure_hash}"

    payment_logger.info(
        "VNPay URL built | txn=%s amount=%s",
        txn.pk, txn.amount_vnd,
    )
    return payment_url


def _build_stripe_url(txn: PaymentTransaction) -> str:
    """
    Create a Stripe Checkout Session and return the session URL.
    Falls back to a placeholder URL if Stripe is not configured.
    """
    stripe_secret = getattr(settings, "STRIPE_SECRET_KEY", "")
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")

    if not stripe_secret:
        payment_logger.warning("Stripe not configured (missing STRIPE_SECRET_KEY) — returning placeholder URL")
        return f"https://checkout.stripe.com/pay?txn={txn.pk}&amount={txn.amount_vnd}"

    try:
        import stripe
        stripe.api_key = stripe_secret

        # Convert VND to cents-equivalent (Stripe uses smallest currency unit)
        # VND is zero-decimal, so amount is passed as-is
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "vnd",
                    "unit_amount": int(txn.amount_vnd),
                    "product_data": {
                        "name": txn.plan.name,
                        "description": f"English Study — {txn.plan.name}",
                    },
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{frontend_url}/payment/success?txn={txn.pk}&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/pricing?cancelled=1",
            metadata={"txn_id": str(txn.pk)},
        )
        payment_logger.info(
            "Stripe session created | txn=%s session=%s",
            txn.pk, session.id,
        )
        return session.url
    except ImportError:
        payment_logger.warning("stripe package not installed — returning placeholder URL")
        return f"https://checkout.stripe.com/pay?txn={txn.pk}"
    except Exception as exc:
        payment_logger.error("Stripe session creation failed | txn=%s err=%s", txn.pk, exc)
        return f"https://checkout.stripe.com/pay?txn={txn.pk}"


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
