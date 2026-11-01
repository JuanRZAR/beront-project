import logging

import psycopg
from flask import g
from pydantic import ValidationError
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm.exc import StaleDataError
from werkzeug.exceptions import HTTPException

from beront.shared.domain.errors import (
    Conflict,
    DomainError,
    Forbidden,
    NotFound,
    Unauthorized,
    Unavailable,
)

STATUS = {
    "INSUFFICIENT_STOCK": 409,
    "IMAGE_TOO_LARGE": 413,
    "INVALID_IMAGE_TYPE": 415,
    "RECOVERY_COOLDOWN": 429,
    "RECOVERY_UNAVAILABLE": 503,
}


def error_response(code, message, status, details=None):
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
            "request_id": getattr(g, "request_id", None),
        }
    }, status


def install_errors(app):
    @app.errorhandler(DomainError)
    def domain_error(error):
        status = STATUS.get(error.code, 422)
        for category, value in (
            (NotFound, 404),
            (Conflict, 409),
            (Unauthorized, 401),
            (Forbidden, 403),
            (Unavailable, 503),
        ):
            if isinstance(error, category):
                status = value
                break
        if isinstance(error, Unauthorized):
            logging.getLogger("beront").warning(
                "identity.access_failed", extra={"request_id": getattr(g, "request_id", None)}
            )
        return error_response(error.code, error.message, status, error.details)

    @app.errorhandler(ValidationError)
    def validation_error(error):
        details = [
            {"field": ".".join(map(str, item["loc"])), "code": item["type"]}
            for item in error.errors(include_input=False, include_url=False, include_context=False)
        ]
        return error_response("VALIDATION_ERROR", "Revisa los campos indicados.", 422, details)

    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        return error_response(
            "DATA_CONFLICT", "El cambio entra en conflicto con los datos existentes.", 409
        )

    @app.errorhandler(StaleDataError)
    def stale_error(error):
        return error_response(
            "VERSION_CONFLICT", "El registro ha cambiado. Recarga los datos.", 409
        )

    @app.errorhandler(DBAPIError)
    @app.errorhandler(psycopg.Error)
    def database_error(error):
        sqlstate = getattr(error, "sqlstate", None) or getattr(
            getattr(error, "orig", None), "sqlstate", None
        )
        if sqlstate in {"40001", "40P01"}:
            return error_response(
                "VERSION_CONFLICT", "Otro cambio está en curso. Recarga los datos.", 409
            )
        if sqlstate in {"23505", "23503", "23514", "23502"}:
            return error_response(
                "DATA_CONFLICT", "El cambio entra en conflicto con los datos existentes.", 409
            )
        logging.getLogger("beront").error(
            "database.unavailable", extra={"request_id": getattr(g, "request_id", None)}
        )
        return error_response(
            "SERVICE_UNAVAILABLE", "El servicio no está disponible temporalmente.", 503
        )

    @app.errorhandler(HTTPException)
    def http_error(error):
        code = {
            400: "BAD_REQUEST",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            413: "PAYLOAD_TOO_LARGE",
            415: "UNSUPPORTED_MEDIA_TYPE",
            429: "RATE_LIMITED",
        }.get(error.code, "HTTP_ERROR")
        if error.code == 429:
            logging.getLogger("beront").warning(
                "security.rate_limit", extra={"request_id": getattr(g, "request_id", None)}
            )
        body, status = error_response(code, "No se pudo procesar la solicitud.", error.code)
        response = app.json.response(body)
        response.status_code = status
        for key, value in error.get_headers():
            if key.lower() in {"retry-after", "allow"}:
                response.headers[key] = value
        return response

    @app.errorhandler(Exception)
    def unexpected_error(error):
        logging.getLogger("beront").error(
            "request.failed.%s",
            type(error).__name__,
            extra={
                "request_id": getattr(g, "request_id", None),
                "exception_type": type(error).__name__,
            },
        )
        return error_response("INTERNAL_ERROR", "Ocurrió un error inesperado.", 500)
