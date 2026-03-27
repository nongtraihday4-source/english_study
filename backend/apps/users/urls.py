"""apps/users/urls.py"""
from django.urls import path

from .views import (
    AdminUserDetailView,
    AdminUserListView,
    ChangePasswordView,
    CookieTokenRefreshView,
    DeviceListView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    RevokeDeviceView,
    UserSettingsView,
    Generate2FAView,
    Verify2FAView,
    Disable2FAView,
)

urlpatterns = [
    # Auth
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/token/refresh/", CookieTokenRefreshView.as_view(), name="auth-token-refresh"),
    # Profile
    path("auth/2fa/generate/", Generate2FAView.as_view(), name="auth-2fa-generate"),
    path("auth/2fa/verify/", Verify2FAView.as_view(), name="auth-2fa-verify"),
    path("auth/2fa/disable/", Disable2FAView.as_view(), name="auth-2fa-disable"),
    
    path("me/", MeView.as_view(), name="me"),
    path("me/password/", ChangePasswordView.as_view(), name="me-change-password"),
    path("me/settings/", UserSettingsView.as_view(), name="me-settings"),
    # Devices (Layer 3)
    path("me/devices/", DeviceListView.as_view(), name="me-devices"),
    path("me/devices/<int:pk>/", RevokeDeviceView.as_view(), name="me-devices-revoke"),
    # Admin
    path("admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/users/<int:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
]
