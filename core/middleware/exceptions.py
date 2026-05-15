import logging

from django.conf import settings
from django.http import JsonResponse

from core.sanitizers import sanitize_user_file_error_message


logger = logging.getLogger(__name__)


class SafeExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:  # pragma: no cover - exercised in integration paths
            logger.exception("Unhandled application exception")
            if settings.DEBUG:
                raise

            accept_header = request.headers.get("Accept", "")
            if "application/json" in accept_header or request.path.startswith("/api/"):
                message = sanitize_user_file_error_message(str(exc), fallback="Internal server error.")
                return JsonResponse({"detail": message}, status=500)
            raise
