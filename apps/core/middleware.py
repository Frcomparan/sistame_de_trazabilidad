import time
import logging

logger = logging.getLogger(__name__)


class AuditMiddleware:
    """Middleware placeholder that records basic request timing and user info.

    This is a minimal implementation: in a later iteration it should persist
    audit events to the database (AuditLog model) and include more context.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start

        try:
            user = getattr(request, 'user', None)
            username = user.username if getattr(user, 'is_authenticated', False) else 'anonymous'
        except Exception:
            username = 'unknown'

        logger.info(
            "AUDIT: user=%s method=%s path=%s status=%s duration=%.3fs",
            username,
            request.method,
            request.get_full_path(),
            getattr(response, 'status_code', 'unknown'),
            duration,
        )

        return response
