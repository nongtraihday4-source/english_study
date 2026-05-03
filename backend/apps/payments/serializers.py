"""
apps/payments/serializers.py
Includes VN currency formatting via fmt_vnd().
"""
from rest_framework import serializers

from utils.formatters import fmt_vnd, fmt_vn
from .models import SubscriptionPlan, UserSubscription, Coupon, PaymentTransaction


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    price_display = serializers.SerializerMethodField()
    original_price_display = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = [
            "id", "name", "name_vi", "billing_period",
            "price_vnd", "price_display",
            "original_price_vnd", "original_price_display",
            "discount_percent",
            "features_json", "max_lessons_per_day",
        ]

    def get_price_display(self, obj):
        return fmt_vnd(int(obj.price_vnd))

    def get_original_price_display(self, obj):
        if obj.original_price_vnd > 0:
            return fmt_vnd(int(obj.original_price_vnd))
        return None

    def get_discount_percent(self, obj):
        if obj.original_price_vnd > 0 and obj.price_vnd < obj.original_price_vnd:
            pct = (1 - obj.price_vnd / obj.original_price_vnd) * 100
            return f"{int(pct)}%"
        return None


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    is_premium = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            "id", "plan", "status", "started_at", "expires_at",
            "auto_renew", "is_premium",
        ]
        read_only_fields = ["__all__"]


class CouponValidateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=30)
    plan_id = serializers.IntegerField()


class CouponValidateResponseSerializer(serializers.ModelSerializer):
    discount_display = serializers.SerializerMethodField()
    final_price_display = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = ["code", "discount_type", "discount_value", "discount_display", "final_price_display"]

    def get_discount_display(self, obj):
        if obj.discount_type == "percent":
            return f"Giảm {obj.discount_value:.0f}%"
        return f"Giảm {fmt_vnd(int(obj.discount_value))}"

    def get_final_price_display(self, obj):
        plan = self.context.get("plan")
        if not plan:
            return None
        price = int(plan.price_vnd)
        if obj.discount_type == "percent":
            after = price * (1 - float(obj.discount_value) / 100)
        else:
            after = max(0, price - int(obj.discount_value))
        return fmt_vnd(int(after))


class CheckoutSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    gateway = serializers.ChoiceField(choices=["vnpay", "stripe"])
    coupon_code = serializers.CharField(max_length=30, required=False, allow_blank=True)
    return_url = serializers.URLField(required=False)


class PaymentTransactionSerializer(serializers.ModelSerializer):
    amount_display = serializers.SerializerMethodField()
    plan_name = serializers.CharField(source="plan.name_vi", read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            "id", "plan", "plan_name", "gateway", "status",
            "amount_vnd", "amount_display", "discount_vnd",
            "gateway_txn_id", "created_at",
        ]

    def get_amount_display(self, obj):
        return fmt_vnd(int(obj.amount_vnd))
