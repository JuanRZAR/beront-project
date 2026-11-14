import re

from beront.shared.domain.errors import DomainError


def validate_message(data):
    for key in ("primary_path", "secondary_path"):
        path = data[key]
        if key == "secondary_path" and not path:
            continue
        if not re.fullmatch(
            r"/(?:catalog/(?:decants|full-bottles)|orders|checkout|products/[a-z0-9]+(?:-[a-z0-9]+)*)(?:\?kind=(?:decant|full_bottle))?",
            path,
        ):
            raise DomainError("INVALID_MESSAGE_LINK", "Selecciona un enlace interno de la tienda.")
    if data["secondary_path"] and any(
        not text["secondary_label"] for text in data["content"].values()
    ):
        raise DomainError(
            "INVALID_MESSAGE_LINK", "Completa el texto del segundo enlace en ES y EN."
        )
    if len(set(data["image_ids"])) != len(data["image_ids"]):
        raise DomainError("INVALID_ASSET", "No repitas imágenes en el mensaje.")
    start, end = data["starts_at"], data["ends_at"]
    if start and end and start >= end:
        raise DomainError("INVALID_MESSAGE_DATES", "La fecha final debe ser posterior al inicio.")


def validate_phone(number):
    if number and (
        not number.isascii()
        or not number.isdigit()
        or not 8 <= len(number) <= 15
        or number.startswith("0")
    ):
        raise DomainError(
            "INVALID_PHONE", "Usa de 8 a 15 dígitos internacionales sin signo ni espacios."
        )
    return number
