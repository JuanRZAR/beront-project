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
