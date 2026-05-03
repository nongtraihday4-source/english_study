"""apps/payments/urls.py"""
from django.urls import path

from .views import (
    CheckoutView,
    CouponValidateView,
    PlanListView,
    StripeWebhookView,
    TransactionListView,
    VNPayWebhookView,
)

urlpatterns = [
    path("plans/", PlanListView.as_view(), name="payment-plans"),
    path("checkout/", CheckoutView.as_view(), name="payment-checkout"),
    path("coupons/validate/", CouponValidateView.as_view(), name="coupon-validate"),
    path("webhooks/vnpay/", VNPayWebhookView.as_view(), name="webhook-vnpay"),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="webhook-stripe"),
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
]
