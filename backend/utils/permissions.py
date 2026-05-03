"""
Layer 4: Role-based & Subscription-based Permissions.
"""
from rest_framework.permissions import BasePermission, IsAuthenticated


class IsAdmin(BasePermission):
    """Only admin users."""
    message = "Chỉ Admin mới có quyền truy cập."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")


class IsTeacher(BasePermission):
    """Teacher or Admin."""
    message = "Chỉ Giáo viên hoặc Admin mới có quyền truy cập."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("teacher", "admin")
        )


class IsStudent(BasePermission):
    """Any authenticated user (student, teacher, admin)."""
    message = "Bạn cần đăng nhập để tiếp tục."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsPremium(BasePermission):
    """Student must have premium account_type."""
    message = "Tính năng này yêu cầu tài khoản Premium."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.account_type == "premium"
        )


class IsOwnerOrAdmin(BasePermission):
    """Object-level: requesting user owns the object, or is admin."""
    message = "Bạn không có quyền thao tác với tài nguyên này."

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == "admin":
            return True
        owner = getattr(obj, "user", getattr(obj, "owner", None))
        return owner == request.user


class IsAdminOrReadOnly(BasePermission):
    """Safe methods (GET) allowed for all; write methods for admin only."""
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")


class IsSupportStaff(BasePermission):
    """Support staff or admin — customer support portal."""
    message = "Chỉ nhân viên hỗ trợ mới có quyền truy cập."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("support", "admin")
        )
