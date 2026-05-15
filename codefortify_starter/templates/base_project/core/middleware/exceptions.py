import logging

from django.conf import settings
from django.http import JsonResponse


logger = logging.getLogger(__name__)


class SafeExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:  # pragma: no cover
            logger.exception("Unhandled application exception")
            if settings.DEBUG:
                raise

            accept_header = request.headers.get("Accept", "")
            if "application/json" in accept_header or request.path.startswith("/api/"):
                return JsonResponse({"detail": str(exc) or "Internal server error."}, status=500)
            raise

