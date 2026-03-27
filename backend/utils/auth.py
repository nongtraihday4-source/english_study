"""
Layer 2: CookieJWTAuthentication
Reads JWT access token from HttpOnly cookie `es_access`.
Falls back to Authorization header for API clients / Swagger.
"""
import logging

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger("es.auth")


class CookieJWTAuthentication(BaseAuthentication):
    """
    Layer 2 — HttpOnly cookie transport.
    Priority: Cookie → Authorization header.

    Design decision on revoked/expired tokens:
    - We return None (AnonymousUser) instead of raising AuthenticationFailed.
    - This is intentional: DRF's AuthenticationFailed bypasses ALL permission
      classes (even AllowAny), causing a permanent 403 lock-out when a browser
      still holds a stale/revoked cookie (e.g. after device revocation).
    - Protected endpoints are still safe: IsAuthenticated will 403 anonymous users.
    - AllowAny endpoints (Login, Register) work normally even with a bad cookie.
    """
    jwt_auth = JWTAuthentication()

    def authenticate(self, request):
        # 1. Try HttpOnly cookie first
        raw_token = request.COOKIES.get(settings.JWT_COOKIE_NAME)

        # 2. Fall back to Authorization: Bearer <token>
        if raw_token is None:
            header_auth = request.META.get("HTTP_AUTHORIZATION", "")
            if header_auth.startswith("Bearer "):
                raw_token = header_auth.split(" ", 1)[1]

        if raw_token is None:
            return None  # No credentials → AnonymousUser

        try:
            validated_token = self.jwt_auth.get_validated_token(raw_token)
            user = self.jwt_auth.get_user(validated_token)
        except (InvalidToken, TokenError) as exc:
            logger.warning("❌ JWT invalid/expired: %s | IP=%s", str(exc), _get_ip(request))
            # Return None instead of raising — browser keeps old expired cookie,
            # raising here would block Login (AllowAny) with a 403.
            return None

        # Layer 3: Check if token JTI is revoked in SessionToken table
        jti = validated_token.get("jti")
        if jti and _is_jti_revoked(jti):
            logger.warning(
                "🚫 Revoked JTI — treating as anonymous | user=%s jti=%s IP=%s",
                user.id, jti, _get_ip(request),
            )
            # Return None (not raise) so AllowAny endpoints (Login) still work.
            # Protected endpoints will correctly 403 via IsAuthenticated.
            return None

        logger.debug("✅ Auth OK | user=%s role=%s IP=%s", user.id, user.role, _get_ip(request))
        # Store JTI on request so LogoutView can revoke this session's token
        request._jti = jti
        return user, validated_token


def _is_jti_revoked(jti: str) -> bool:
    """Layer 3: Check SessionToken revocation table."""
    from apps.users.models import SessionToken
    return SessionToken.objects.filter(jti=jti, is_revoked=True).exists()


def _get_ip(request) -> str:
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")
