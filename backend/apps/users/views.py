"""
apps/users/views.py
─────────────────────────────────────────────────────────────────────────────
Auth Endpoints:
  POST /api/auth/register/
  POST /api/auth/login/          → sets HttpOnly cookies
  POST /api/auth/logout/         → blacklists token + clears cookies
  POST /api/auth/token/refresh/  → rotates refresh token (in cookie)
  GET/PATCH /api/me/
  PATCH /api/me/password/
  GET/DELETE /api/me/devices/    → list / revoke active sessions
─────────────────────────────────────────────────────────────────────────────
"""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from utils.permissions import IsAdmin
from .models import SessionToken, UserSettings
from .serializers import (
    AdminUserListSerializer,
    ChangePasswordSerializer,
    RegisterSerializer,
    SessionTokenSerializer,
    UserMeSerializer,
    UserSettingsSerializer,
)

User = get_user_model()
auth_logger = logging.getLogger("es.auth")


def _set_jwt_cookies(response: Response, access: str, refresh: str) -> None:
    response.set_cookie(
        settings.JWT_COOKIE_NAME, access,
        max_age=settings.JWT_COOKIE_MAX_AGE,
        httponly=settings.JWT_COOKIE_HTTPONLY,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )
    response.set_cookie(
        settings.JWT_REFRESH_COOKIE_NAME, refresh,
        max_age=settings.JWT_REFRESH_COOKIE_MAX_AGE,
        httponly=settings.JWT_COOKIE_HTTPONLY,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )


def _clear_jwt_cookies(response: Response) -> None:
    response.delete_cookie(settings.JWT_COOKIE_NAME)
    response.delete_cookie(settings.JWT_REFRESH_COOKIE_NAME)


# ── Register ──────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "login"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        response = Response(
            {"message": "Đăng ký thành công!", "user_id": user.pk},
            status=status.HTTP_201_CREATED,
        )
        _set_jwt_cookies(response, str(refresh.access_token), str(refresh))
        return response


# ── Login ─────────────────────────────────────────────────────────────────────

class LoginView(APIView):
    """
    Layer 2 + 3: Issues JWT pair into HttpOnly cookies.
    Stores SessionToken for per-device JTI revocation.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        from apps.users.serializers import CustomTokenObtainPairSerializer

        serializer = CustomTokenObtainPairSerializer(
            data=request.data, context={"request": request}
        )
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            auth_logger.warning("Login failed | ip=%s reason=%s", request.META.get("REMOTE_ADDR"), str(exc))
            raise InvalidToken(exc.args[0])

        tokens = serializer.validated_data
        access_token_str = tokens["access"]
        refresh_token_str = tokens["refresh"]
        user_data = tokens["user"]

        # Layer 3: persist JTI in SessionToken table
        from rest_framework_simplejwt.tokens import AccessToken as JWTAccessToken
        from datetime import datetime, timezone as dt_timezone
        decoded = JWTAccessToken(access_token_str)
        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
        device = request.META.get("HTTP_USER_AGENT", "")[:200]
        exp_ts = decoded["exp"]
        expires_at = datetime.fromtimestamp(exp_ts, tz=dt_timezone.utc)

        SessionToken.objects.create(
            user_id=user_data["id"],
            jti=decoded["jti"],
            device_name=device,
            ip_address=ip[:45],
            expires_at=expires_at,
        )

        auth_logger.info(
            "Login SUCCESS | user=%s ip=%s device=%s",
            user_data["id"], ip[:15], device[:60],
        )

        response = Response({"message": "Đăng nhập thành công!", "user": user_data})
        _set_jwt_cookies(response, access_token_str, refresh_token_str)
        return response


# ── Logout ────────────────────────────────────────────────────────────────────

class LogoutView(APIView):
    """Blacklists refresh token, revokes SessionToken, clears cookies.
    AllowAny: cookies must ALWAYS be cleared even if the token is already
    expired or revoked — prevents the 403 loop on re-login.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Layer 1: simplejwt blacklist
            except Exception:
                pass  # Already invalid — fine

        # Layer 3: revoke this session's JTI
        jti = getattr(request, "_jti", None)
        if jti:
            SessionToken.objects.filter(jti=jti).update(is_revoked=True)

        auth_logger.info("Logout | user=%s", request.user.pk)
        response = Response({"message": "Đăng xuất thành công!"})
        _clear_jwt_cookies(response)
        return response


# ── Token Refresh ─────────────────────────────────────────────────────────────

class CookieTokenRefreshView(APIView):
    """Reads refresh token from HttpOnly cookie, returns new pair."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if not refresh_token:
            return Response({"detail": "Refresh token không tìm thấy."}, status=401)

        serializer = TokenRefreshSerializer(
            data={"refresh": refresh_token},
            context={"request": request},
        )
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0])

        response = Response({"message": "Token đã gia hạn."})
        _set_jwt_cookies(
            response,
            serializer.validated_data["access"],
            serializer.validated_data.get("refresh", refresh_token),
        )
        return response


# ── Me ────────────────────────────────────────────────────────────────────────

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserSettingsView(APIView):
    """
    GET/PATCH /api/me/settings/
    Returns or updates the current user’s notification / UI settings.
    """
    permission_classes = [permissions.IsAuthenticated]

    def _get_or_create_settings(self, user):
        settings_obj, _ = UserSettings.objects.get_or_create(user=user)
        return settings_obj

    def get(self, request):
        obj = self._get_or_create_settings(request.user)
        return Response(UserSettingsSerializer(obj).data)

    def patch(self, request):
        obj = self._get_or_create_settings(request.user)
        serializer = UserSettingsSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Đổi mật khẩu thành công."})


# ── Devices ───────────────────────────────────────────────────────────────────

class DeviceListView(generics.ListAPIView):
    serializer_class = SessionTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SessionToken.objects.filter(
            user=self.request.user, is_revoked=False
        ).order_by("-created_at")


class RevokeDeviceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            token = SessionToken.objects.get(pk=pk, user=request.user)
        except SessionToken.DoesNotExist:
            return Response({"detail": "Thiết bị không tồn tại."}, status=404)
        token.is_revoked = True
        token.save(update_fields=["is_revoked"])
        auth_logger.info("Device revoked | user=%s session=%s", request.user.pk, pk)
        return Response({"message": "Thiết bị đã bị thu hồi."})


# ── Admin user management ─────────────────────────────────────────────────────

class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ["role", "account_type", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["date_joined", "last_login", "email"]

    def get_queryset(self):
        return User.objects.filter(is_deleted=False).select_related("profile")


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.filter(is_deleted=False)


# ── 2FA (Two-Factor Authentication) ──────────────────────────────────────────

import pyotp
import qrcode
import base64
from io import BytesIO

class Generate2FAView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        settings_obj, _ = UserSettings.objects.get_or_create(user=user)

        if settings_obj.is_2fa_enabled:
            return Response({"detail": "2FA đã được bật."}, status=400)

        secret = pyotp.random_base32()
        settings_obj.totp_secret = secret
        settings_obj.save()

        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(name=user.email, issuer_name="EnglishStudy")
        
        qr = qrcode.make(provisioning_uri)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        return Response({
            "secret": secret,
            "qr_code": f"data:image/png;base64,{qr_b64}"
        })


class Verify2FAView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_code = request.data.get("otp_code")
        if not otp_code:
            return Response({"detail": "Vui lòng cung cấp mã OTP."}, status=400)

        settings_obj, _ = UserSettings.objects.get_or_create(user=user)
        if not settings_obj.totp_secret:
            return Response({"detail": "Chưa khởi tạo 2FA. Vui lòng thử lại."}, status=400)

        totp = pyotp.TOTP(settings_obj.totp_secret)
        if totp.verify(otp_code):
            settings_obj.is_2fa_enabled = True
            settings_obj.save()
            auth_logger.info("2FA Enabled | user=%s", user.pk)
            return Response({"message": "Bật xác thực 2 lớp thành công."})
        else:
            return Response({"detail": "Mã OTP không hợp lệ."}, status=400)


class Disable2FAView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        password = request.data.get("password")
        if not password or not user.check_password(password):
            return Response({"detail": "Mật khẩu không đúng."}, status=400)

        settings_obj, _ = UserSettings.objects.get_or_create(user=user)
        settings_obj.is_2fa_enabled = False
        settings_obj.totp_secret = None
        settings_obj.save()
            
        auth_logger.info("2FA Disabled | user=%s", user.pk)
        return Response({"message": "Đã tắt xác thực 2 lớp thành công."})
