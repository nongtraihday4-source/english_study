"""
apps/users/serializers.py
Includes CustomTokenObtainPairSerializer — referenced by settings.SIMPLE_JWT.
"""
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserProfile, UserSettings, SessionToken

User = get_user_model()
auth_logger = logging.getLogger("es.auth")


# ── JWT ──────────────────────────────────────────────────────────────────────

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Layer 2 + 4: Adds role/account_type/level claims to JWT so clients can
    make permission decisions without extra round-trips.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Custom claims baked into access token
        token["role"] = user.role
        token["account_type"] = user.account_type
        token["current_level"] = user.current_level
        token["display_name"] = user.get_full_name() or user.email
        auth_logger.debug(
            "JWT issued | user=%s role=%s account_type=%s",
            user.pk, user.role, user.account_type,
        )
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # --- 2FA Check ---
        if hasattr(user, 'settings') and getattr(user.settings, 'is_2fa_enabled', False):
            otp_code = self.initial_data.get("otp_code")
            if not otp_code:
                raise serializers.ValidationError({"requires_2fa": True, "detail": "Vui lòng nhập mã OTP 2 lớp."})
            import pyotp
            totp = pyotp.TOTP(user.settings.totp_secret)
            if not totp.verify(otp_code):
                raise serializers.ValidationError({"otp_code": "Mã xác thực 2 lớp không hợp lệ."})
        # -----------------

        data["user"] = {
            "id": user.pk,
            "email": user.email,
            "full_name": user.get_full_name(),
            "role": user.role,
            "account_type": user.account_type,
            "current_level": user.current_level,
        }
        return data


# ── User Serializers ───────────────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ["user"]


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        exclude = ["user"]


class UserMeSerializer(serializers.ModelSerializer):
    """Full self-profile read/write — used for GET/PATCH /api/me/."""
    profile = UserProfileSerializer()
    settings = UserSettingsSerializer()

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name",
            "role", "account_type", "current_level", "target_level",
            "date_joined", "profile", "settings",
        ]
        read_only_fields = ["id", "email", "role", "date_joined"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        settings_data = validated_data.pop("settings", {})

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        if profile_data:
            UserProfile.objects.filter(user=instance).update(**profile_data)
        if settings_data:
            UserSettings.objects.filter(user=instance).update(**settings_data)

        return instance


class UserPublicSerializer(serializers.ModelSerializer):
    """Minimal public profile (for leaderboard, comments)."""
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "current_level", "avatar_url"]

    def get_avatar_url(self, obj):
        try:
            return obj.profile.avatar_url
        except Exception:
            return None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Xác nhận mật khẩu")

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password2": "Mật khẩu xác nhận không khớp."})
        return attrs

    def create(self, validated_data):
        # Auto-generate username from email (email is the login field)
        email = validated_data["email"]
        username = email.split("@")[0]
        # Ensure uniqueness
        from django.contrib.auth import get_user_model
        _User = get_user_model()
        base = username
        counter = 1
        while _User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
        validated_data["username"] = username
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        UserSettings.objects.create(user=user)
        auth_logger.info("New user registered | user=%s email=%s", user.pk, user.email)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mật khẩu cũ không đúng.")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(self.context["request"], user)
        auth_logger.info("Password changed | user=%s", user.pk)


class SessionTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionToken
        fields = ["id", "device_name", "ip_address", "created_at", "expires_at"]


class AdminUserListSerializer(serializers.ModelSerializer):
    """Admin-only serializer with all fields."""
    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "role",
            "account_type", "current_level", "is_active", "date_joined", "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]
