from dataclasses import replace

from sqlalchemy.exc import OperationalError

from beront.app import create_app


def test_uniform_errors_headers_and_limits(client):
    assert (
        client.post(
            "/api/v1/cart/quote", data="broken", content_type="application/json"
        ).status_code
        == 400
    )
    assert (
        client.post("/api/v1/cart/quote", data="{}", content_type="text/plain").status_code == 415
    )
    assert (
        client.post(
            "/api/v1/cart/quote", data=" " * 65537, content_type="application/json"
        ).status_code
        == 413
    )
    response = client.get("/not-found")
    assert response.status_code == 404
    assert response.json["error"]["request_id"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert "Access-Control-Allow-Origin" not in response.headers
    assert client.get("/api/v1/cart/quote").status_code == 405
    assert (
        client.get("/api/v1/catalog/products", headers={"Host": "evil.example"}).status_code == 400
    )


def test_private_api_requires_authentication(client):
    for path in (
        "/api/v1/admin/products",
        "/api/v1/admin/brands",
        "/api/v1/admin/inventory",
        "/api/v1/admin/inventory/movements",
        "/api/v1/auth/session",
    ):
        assert client.get(path).status_code == 401


def test_fail_closed_and_exception_redaction(app, client, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("SECRET MUST NEVER LEAK")

    monkeypatch.setattr(app.extensions["beront"].queries, "facets", fail)
    response = client.get("/api/v1/catalog/facets")
    assert response.status_code == 500
    assert "SECRET" not in response.text

    def database_down(*args, **kwargs):
        raise OperationalError("SELECT private", {}, Exception("PASSWORD"))

    monkeypatch.setattr(app.extensions["beront"].queries, "facets", database_down)
    response = client.get("/api/v1/catalog/facets")
    assert response.status_code == 503
    assert "PASSWORD" not in response.text and "SELECT" not in response.text


def test_login_rate_limit(settings):
    app = create_app(replace(settings, rate_limits=True))
    client = app.test_client()
    token = client.get("/api/v1/auth/csrf").json["data"]["csrf_token"]
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "missing", "password": "invalid"},
            headers={"X-CSRFToken": token},
        )
        assert response.status_code == 401
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "missing", "password": "invalid"},
        headers={"X-CSRFToken": token},
    )
    assert response.status_code == 429
    app.extensions["beront"].engine.dispose()
