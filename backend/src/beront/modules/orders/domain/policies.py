import base64
import hashlib
import hmac
import json

from beront.shared.domain.errors import Conflict, DomainError

RECOVERY_COOLDOWN_SECONDS = 600


def fingerprint(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def sign_quote(snapshot, secret):
    payload = (
        base64.urlsafe_b64encode(
            json.dumps(
                snapshot, sort_keys=True, separators=(",", ":"), default=str, ensure_ascii=False
            ).encode()
        )
        .decode()
        .rstrip("=")
    )
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token = payload + "." + signature
    if len(token) > 57344:
        raise DomainError(
            "CHECKOUT_NOT_CONFIGURED", "Contacta al propietario para completar esta compra."
        )
    return token


def verify_quote(token, secret):
    try:
        payload, signature = token.split(".")
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Signature mismatch")
        return json.loads(
            base64.b64decode(payload + "=" * (-len(payload) % 4), altchars=b"-_", validate=True)
        )
    except (ValueError, UnicodeError) as error:
        raise Conflict(
            "QUOTE_CHANGED", "La cotización no es válida; vuelve a revisar el resumen."
        ) from error


def ensure_transition(order, target):
    phase = target["phase"]
    if not target["active"]:
        raise Conflict("INVALID_TRANSITION", "El estado de destino está desactivado.")
    paid = order["paid_at"] is not None
    if phase in {"paid", "shipped", "delivered"} and not paid:
        raise Conflict(
            "PAYMENT_REQUIRED", "Primero valida el pago mediante la acción de aprobación."
        )
    if phase == "stock_issue" and order["payment_state"] != "stock_issue":
        raise Conflict(
            "PAYMENT_REQUIRED", "La incidencia de stock se registra al revisar un pago real."
        )
    if paid and phase in {"awaiting_payment", "stock_issue", "cancelled"}:
        raise Conflict(
            "INVALID_TRANSITION",
            "Una venta confirmada requiere un flujo de devolución, fuera de esta versión.",
        )
    if phase in {"shipped", "delivered"} and not (
        order["guide_number"] and order["tracking_number"]
    ):
        raise Conflict(
            "TRACKING_REQUIRED",
            "Registra la guía y el código de seguimiento antes de marcar el envío.",
        )
