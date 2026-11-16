import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy.engine import make_url

LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}
PROFILES = {"local", "production"}


@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: str
    frontend_origin: str = "http://localhost:4321"
    storage_root: Path = Path(__file__).resolve().parents[2] / "var"
    testing: bool = False
    rate_limits: bool = True
    cart_requires_stock: bool = True
    smtp_host: str = ""
    smtp_port: int = 25
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_sender: str = ""
    smtp_security: str = "none"
    environment: str = "local"

    @property
    def production(self):
        return self.environment == "production"

    def __post_init__(self):
        if self.environment not in PROFILES:
            raise ValueError("APP_ENV debe ser local o production.")
        url = make_url(self.database_url)
        if url.drivername != "postgresql+psycopg":
            raise ValueError("DATABASE_URL debe usar PostgreSQL con psycopg.")
        if not self.production and url.host not in LOOPBACK_HOSTS:
            raise ValueError("DATABASE_URL debe apuntar a PostgreSQL local con psycopg.")
        if self.production and not url.host:
            raise ValueError("DATABASE_URL debe indicar el servidor de PostgreSQL.")
        if len(self.secret_key) < 32 or self.secret_key.lower().startswith(("replace", "cambiar")):
            raise ValueError("SECRET_KEY debe contener al menos 32 caracteres aleatorios.")
        if self.smtp_host:
            if not 1 <= self.smtp_port <= 65535:
                raise ValueError("SMTP_PORT debe estar entre 1 y 65535.")
            if self.smtp_security not in {"none", "starttls", "ssl"}:
                raise ValueError("SMTP_SECURITY debe ser none, starttls o ssl.")
            if not re.fullmatch(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", self.smtp_sender):
                raise ValueError("SMTP_SENDER debe ser un correo válido.")
            if bool(self.smtp_username) != bool(self.smtp_password):
                raise ValueError("SMTP_USERNAME y SMTP_PASSWORD se configuran juntos.")
        origin = urlparse(self.frontend_origin)
        local_origin = origin.scheme == "http" and origin.hostname in LOOPBACK_HOSTS
        if self.production:
            if not (local_origin or (origin.scheme == "https" and origin.hostname)):
                raise ValueError("FRONTEND_ORIGIN debe ser un origen HTTPS.")
        elif not local_origin:
            raise ValueError("FRONTEND_ORIGIN debe ser un origen HTTP local.")
        if origin.path not in {"", "/"} or origin.query or origin.fragment or origin.username:
            raise ValueError("FRONTEND_ORIGIN no puede contener rutas ni credenciales.")

    @classmethod
    def from_env(cls):
        environment = os.getenv("APP_ENV", "local")
        if environment not in PROFILES:
            raise ValueError("APP_ENV debe ser local o production.")
        return cls(
            environment=environment,
            database_url=os.environ["DATABASE_URL"],
            secret_key=os.environ["SECRET_KEY"],
            frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:4321"),
            cart_requires_stock=flag("CART_REQUIRES_STOCK", "true"),
            smtp_host=os.getenv("SMTP_HOST", ""),
            smtp_port=int(os.getenv("SMTP_PORT", "25")),
            smtp_username=os.getenv("SMTP_USERNAME", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            smtp_sender=os.getenv("SMTP_SENDER", ""),
            smtp_security=os.getenv("SMTP_SECURITY", "none").lower(),
        )


def flag(name, default):
    value = os.getenv(name, default).lower()
    if value not in {"true", "false"}:
        raise ValueError(f"{name} debe ser true o false.")
    return value == "true"
