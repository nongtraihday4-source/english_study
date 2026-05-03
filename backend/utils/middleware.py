"""Request/Response logging middleware."""
import logging
import time

logger = logging.getLogger("es.auth")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        elapsed = (time.monotonic() - start) * 1000

        # Only log API calls, skip static/media
        if request.path.startswith("/api/"):
            user_id = getattr(getattr(request, "user", None), "id", "anon")
            logger.debug(
                "%s %s | user=%s status=%s elapsed=%.0fms",
                request.method,
                request.path,
                user_id,
                response.status_code,
                elapsed,
            )
        return response
