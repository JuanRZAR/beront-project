import secrets

import pytest

from beront.config import Settings


@pytest.mark.parametrize(
    "overrides",
    [
        {"database_url": "sqlite:///not-allowed.db"},
        {"database_url": "postgresql+psycopg://remote.example/beront"},
        {"secret_key": "short"},
        {"frontend_origin": "https://remote.example"},
        {"frontend_origin": "http://localhost:4321/path"},
        {"smtp_host": "localhost", "smtp_sender": "no-es-un-correo"},
        {"smtp_host": "localhost", "smtp_sender": "a@example.test", "smtp_port": 0},
        {"smtp_host": "localhost", "smtp_sender": "a@example.test", "smtp_security": "tls"},
        {"smtp_host": "localhost", "smtp_sender": "a@example.test", "smtp_username": "usuario"},
    ],
)
def test_configuration_rejects_unsafe_values(overrides):
    values = {
        "database_url": "postgresql+psycopg://localhost/beront",
        "secret_key": secrets.token_urlsafe(32),
    }
    with pytest.raises(ValueError):
        Settings(**(values | overrides))


def test_environment_requires_explicit_local_profile(monkeypatch):
    monkeypatch.setenv("APP_ENV", "public")
    with pytest.raises(ValueError):
        Settings.from_env()
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost/beront")
    monkeypatch.setenv("SECRET_KEY", secrets.token_urlsafe(32))
    monkeypatch.setenv("WHATSAPP_NUMBER", "not-a-setting")
    assert not hasattr(Settings.from_env(), "whatsapp_number")


def test_smtp_is_read_from_the_environment(monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost/beront")
    monkeypatch.setenv("SECRET_KEY", secrets.token_urlsafe(32))
    monkeypatch.setenv("SMTP_HOST", "127.0.0.1")
    monkeypatch.setenv("SMTP_PORT", "1025")
    monkeypatch.setenv("SMTP_SENDER", "tienda@example.test")
    settings = Settings.from_env()
    assert (settings.smtp_host, settings.smtp_port, settings.smtp_security) == (
        "127.0.0.1",
        1025,
        "none",
    )
    monkeypatch.delenv("SMTP_HOST")
    assert Settings.from_env().smtp_host == ""


def test_cart_stock_validation_is_strict_by_default_and_explicitly_configurable(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost/beront")
    monkeypatch.setenv("SECRET_KEY", secrets.token_urlsafe(32))
    monkeypatch.delenv("CART_REQUIRES_STOCK", raising=False)
    assert Settings.from_env().cart_requires_stock
    monkeypatch.setenv("CART_REQUIRES_STOCK", "false")
    assert not Settings.from_env().cart_requires_stock
    monkeypatch.setenv("CART_REQUIRES_STOCK", "true")
    assert Settings.from_env().cart_requires_stock
    monkeypatch.setenv("CART_REQUIRES_STOCK", "typo")
    with pytest.raises(ValueError, match="CART_REQUIRES_STOCK"):
        Settings.from_env()


PRODUCTION = {
    "database_url": "postgresql+psycopg://beront:x@postgres:5432/beront",
    "frontend_origin": "https://beront.com",
    "environment": "production",
}


@pytest.mark.parametrize(
    "overrides",
    [
        {"environment": "staging"},
        {"database_url": "postgresql+psycopg:///beront"},
        {"database_url": "postgresql://beront:x@postgres:5432/beront"},
        {"frontend_origin": "http://beront.com"},
        {"frontend_origin": "https://beront.com/path"},
        {"frontend_origin": "https://"},
    ],
)
def test_production_profile_rejects_unsafe_values(overrides):
    with pytest.raises(ValueError):
        Settings(secret_key=secrets.token_urlsafe(32), **(PRODUCTION | overrides))


def test_production_profile_accepts_remote_database_and_https_origin(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", PRODUCTION["database_url"])
    monkeypatch.setenv("FRONTEND_ORIGIN", PRODUCTION["frontend_origin"])
    monkeypatch.setenv("SECRET_KEY", secrets.token_urlsafe(32))
    assert Settings.from_env().production


def test_local_profile_keeps_local_database(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.setenv("DATABASE_URL", PRODUCTION["database_url"])
    monkeypatch.setenv("SECRET_KEY", secrets.token_urlsafe(32))
    with pytest.raises(ValueError):
        Settings.from_env()
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost/beront")
    assert not Settings.from_env().production
