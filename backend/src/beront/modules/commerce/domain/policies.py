from beront.shared.domain.errors import DomainError


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
