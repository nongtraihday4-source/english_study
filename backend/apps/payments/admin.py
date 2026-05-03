from django.contrib import admin

from .models import Coupon, CouponRedemption, PaymentTransaction, SubscriptionPlan, UserSubscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ["name_vi", "billing_period", "price_vnd", "is_active", "sort_order"]
    list_filter = ["billing_period", "is_active"]


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "status", "started_at", "expires_at", "auto_renew"]
    list_filter = ["status", "plan"]
    search_fields = ["user__email"]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "discount_type", "discount_value", "used_count", "max_uses", "is_active", "expires_at"]
    list_filter = ["discount_type", "is_active"]
    search_fields = ["code"]


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "gateway", "status", "amount_vnd", "created_at"]
    list_filter = ["gateway", "status"]
    search_fields = ["user__email", "gateway_txn_id"]
    readonly_fields = ["gateway_response_json"]
