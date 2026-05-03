"""Global DRF exception handler with Vietnamese error messages."""
import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("es.auth")

_VN_STATUS = {
    400: "Dữ liệu gửi lên không hợp lệ.",
    401: "Bạn chưa đăng nhập hoặc phiên đăng nhập đã hết hạn.",
    403: "Bạn không có quyền thực hiện thao tác này.",
    404: "Không tìm thấy tài nguyên yêu cầu.",
    405: "Phương thức HTTP không được hỗ trợ.",
    429: "Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau.",
    500: "Lỗi máy chủ nội bộ. Vui lòng liên hệ hỗ trợ.",
}


def custom_exception_handler(exc, context):
    # Let DRF handle standard exceptions first
    response = exception_handler(exc, context)

    if isinstance(exc, Http404):
        response = Response(status=status.HTTP_404_NOT_FOUND)
    elif isinstance(exc, PermissionDenied):
        response = Response(status=status.HTTP_403_FORBIDDEN)

    if response is not None:
        code = response.status_code
        detail = response.data

        # Normalise `detail` to a list of strings for consistent frontend parsing
        if isinstance(detail, dict):
            errors = {}
            for field, msgs in detail.items():
                if isinstance(msgs, list):
                    errors[field] = [str(m) for m in msgs]
                else:
                    errors[field] = [str(msgs)]
            error_payload = errors
        else:
            error_payload = [str(detail)]

        response.data = {
            "success": False,
            "status_code": code,
            "message": _VN_STATUS.get(code, "Đã xảy ra lỗi."),
            "errors": error_payload,
        }

        if code >= 500:
            logger.error("5xx error | %s | %s", context.get("view"), exc)

    return response
