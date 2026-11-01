class DomainError(Exception):
    def __init__(self, code: str, message: str, details: list | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or []


class NotFound(DomainError):
    def __init__(self):
        super().__init__("NOT_FOUND", "Recurso no encontrado.")


class Conflict(DomainError):
    def __init__(
        self, code="VERSION_CONFLICT", message="El registro ha cambiado. Recarga los datos."
    ):
        super().__init__(code, message)


class Unauthorized(DomainError):
    def __init__(self):
        super().__init__("UNAUTHORIZED", "La sesión o las credenciales no son válidas.")


class Forbidden(DomainError):
    def __init__(self):
        super().__init__("FORBIDDEN", "No tienes permiso para realizar esta acción.")


class Unavailable(DomainError):
    def __init__(self):
        super().__init__("SERVICE_UNAVAILABLE", "El servicio no está disponible temporalmente.")
