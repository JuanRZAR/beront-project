from datetime import timedelta
from unittest.mock import patch

import pytest
from sqlalchemy import text

from beront.shared.domain.errors import Conflict, NotFound, Unauthorized

PASSWORD = "Temporary test password 12345"


def test_login_requires_csrf_and_generic_credentials(client, admin):
    assert (
        client.post(
            "/api/v1/auth/login", json={"username": admin.username, "password": PASSWORD}
        ).status_code
        == 403
    )
    token = client.get("/api/v1/auth/csrf").json["data"]["csrf_token"]
    headers = {"X-CSRFToken": token}
    for username in (admin.username, "missing"):
        response = client.post(
            "/api/v1/auth/login", json={"username": username, "password": "wrong"}, headers=headers
        )
        assert response.status_code == 401
        assert "password" not in str(response.json)
    response = client.post(
        "/api/v1/auth/login",
        json={"username": admin.username, "password": PASSWORD},
        headers={**headers, "Origin": "https://evil.example"},
    )
    assert response.status_code == 403


def test_session_logout_cookies_and_revocation(app, client, auth, database):
    response = client.get("/api/v1/auth/session")
    assert response.json["data"]["role"] == "admin"
    assert response.headers["Cache-Control"] == "no-store"
    cookie = client.get_cookie("beront_session")
    assert cookie.http_only and cookie.same_site == "Lax"
    copied_cookie = cookie.value
    with database[2].connect() as connection:
        records = connection.execute(text("SELECT token_hash FROM admin_sessions")).all()
        assert len(records) == 1
        assert len(records[0].token_hash) == 64
    assert client.post("/api/v1/auth/logout", headers=auth).status_code == 204
    client.set_cookie("beront_session", copied_cookie)
    assert client.get("/api/v1/auth/session").status_code == 401


def test_expiry_reset_and_inactive_admin(app, admin):
    service = app.extensions["beront"].identity
    _, token = service.login(admin.username, PASSWORD)
    now = service.clock()
    with patch.object(service, "clock", return_value=now + timedelta(minutes=30)):
        with pytest.raises(Unauthorized):
            service.authenticate(token)
    _, fresh = service.login(admin.username, PASSWORD)
    service.reset_password(admin.username, "New temporary password 12345")
    with pytest.raises(Unauthorized):
        service.authenticate(fresh)
    with pytest.raises(Unauthorized):
        service.login(admin.username, PASSWORD)
    service.login(admin.username, "New temporary password 12345")
    with pytest.raises(NotFound):
        service.reset_password("missing", PASSWORD)


def test_cli_and_duplicate_administrators(app, admin):
    service = app.extensions["beront"].identity
    with pytest.raises(Conflict):
        service.create_admin(admin.username, PASSWORD)
    with pytest.raises(ValueError):
        service.create_admin("", PASSWORD)
    runner = app.test_cli_runner()
    result = runner.invoke(
        args=["create-admin", "cli-admin"], input=PASSWORD + "\n" + PASSWORD + "\n"
    )
    assert result.exit_code != 0 and "administrador" in result.output
    result = runner.invoke(
        args=["reset-password", admin.username], input=PASSWORD + "\n" + PASSWORD + "\n"
    )
    assert result.exit_code == 0
    result = runner.invoke(
        args=["create-admin", "cli-admin"], input=PASSWORD + "\n" + PASSWORD + "\n"
    )
    assert result.exit_code != 0
    result = runner.invoke(
        args=["reset-password", "missing"], input=PASSWORD + "\n" + PASSWORD + "\n"
    )
    assert result.exit_code != 0


def test_permission_enforcement(app, client, auth, monkeypatch):
    import beront.modules.identity.presentation.decorators as authorization

    monkeypatch.setattr(authorization, "PERMISSIONS", frozenset())
    assert client.get("/api/v1/admin/products").status_code == 403
    client.delete_cookie("beront_session")
    assert client.get("/api/v1/admin/products").status_code == 401


def test_rotates_session_on_login(app, client, auth, admin):
    old = client.get_cookie("beront_session").value
    response = client.post(
        "/api/v1/auth/login", json={"username": admin.username, "password": PASSWORD}, headers=auth
    )
    assert response.status_code == 200
    assert client.get_cookie("beront_session").value != old
    client.set_cookie("beront_session", old)
    assert client.get("/api/v1/auth/session").status_code == 401


def test_auth_rejects_blank_long_and_disabled(app, admin, database):
    service = app.extensions["beront"].identity
    for token in ("", "x" * 129, "nonexistent"):
        with pytest.raises(Unauthorized):
            service.authenticate(token)
    _, token = service.login(admin.username, PASSWORD)
    with database[2].begin() as connection:
        connection.execute(
            text("UPDATE administrators SET active=false WHERE id=:id"), {"id": admin.id}
        )
    with pytest.raises(Unauthorized):
        service.authenticate(token)
    with pytest.raises(Unauthorized):
        service.login(admin.username, PASSWORD)
    service.logout("missing-token")
