import ipaddress
from uuid import uuid4

from flask import g, request
from flask_wtf.csrf import CSRFError

from beront.shared.presentation.errors import error_response

LOOPBACK = {"127.0.0.1", "::1"}


def client_address():
    forwarded = request.headers.get("X-Client-IP")
    if forwarded and request.remote_addr in LOOPBACK:
        try:
            return str(ipaddress.ip_address(forwarded.strip()))
        except ValueError:
            pass
    return request.remote_addr or "unknown"


def install_security(app, settings):
    @app.before_request
    def request_context():
        g.request_id = str(uuid4())
        if (
            request.method == "POST"
            and request.mimetype == "multipart/form-data"
            and (
                request.path.endswith(("/images", "/receipts"))
                or request.path in {"/api/v1/admin/media", "/api/v1/orders"}
            )
        ):
            request.max_content_length = 5 * 1024 * 1024 + 65536
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("Origin")
            if origin and origin != settings.frontend_origin.rstrip("/"):
                return error_response("FORBIDDEN_ORIGIN", "Origen no autorizado.", 403)

    @app.after_request
    def headers(response):
        response.headers["X-Request-ID"] = getattr(g, "request_id", str(uuid4()))
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        )
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if any(
            part in request.path
            for part in ("/admin/", "/auth/", "/cart/", "/orders", "/checkout/")
        ):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return error_response(
            "CSRF_INVALID", "La protección de sesión expiró. Recarga e inténtalo otra vez.", 403
        )
