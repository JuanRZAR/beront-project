import io

from PIL import Image
from sqlalchemy import text


def photograph():
    data = io.BytesIO()
    Image.new("RGB", (15, 20), "#B8A58A").save(data, "PNG")
    data.seek(0)
    return data


def upload(client, auth):
    return client.post(
        "/api/v1/admin/media",
        data={"name": "Fotografía de prueba", "file": (photograph(), "../../photo.png")},
        headers=auth,
    )


def test_library_upload_is_deduplicated_and_url_is_persisted(app, client, auth, database):
    first, second = upload(client, auth), upload(client, auth)
    assert first.status_code == 201 and second.status_code == 200
    assert first.json["data"]["id"] == second.json["data"]["id"]
    assert len(list(app.extensions["beront"].storage.uploads.iterdir())) == 1
    with database[2].connect() as connection:
        row = connection.execute(text("SELECT url,checksum FROM media_assets")).one()
        assert row.url == first.json["data"]["url"] and len(row.checksum) == 64
    assert app.test_client().get(first.json["data"]["url"]).status_code == 404
    assert client.get(first.json["data"]["url"], buffered=True).status_code == 200


def test_one_library_photo_can_be_assigned_to_two_perfumes(app, client, auth, sample):
    product, _ = sample
    asset = upload(client, auth).json["data"]
    path = "/api/v1/admin/products/" + str(product.id) + "/images"
    first = client.post(path, json={"asset_id": asset["id"], "alt_es": "Foto"}, headers=auth)
    assert first.status_code == 201
    assert app.test_client().get(asset["url"], buffered=True).status_code == 200
    second_product = client.post(
        "/api/v1/admin/products",
        json={
            "brand_id": str(product.brand_id),
            "name": "Otro perfume de prueba",
            "slug": "otro-perfume-prueba",
            "audience": "unisex",
        },
        headers=auth,
    ).json["data"]
    second = client.post(
        "/api/v1/admin/products/" + second_product["id"] + "/images",
        json={"asset_id": asset["id"]},
        headers=auth,
    )
    assert second.status_code == 201
    assert len(list(app.extensions["beront"].storage.uploads.iterdir())) == 1
    assert (
        client.delete(
            "/api/v1/admin/media/" + asset["id"], json={"version": 1}, headers=auth
        ).status_code
        == 409
    )
    assert (
        client.delete(
            "/api/v1/admin/images/" + first.json["data"]["id"], json={"version": 1}, headers=auth
        ).status_code
        == 204
    )
    assert app.test_client().get(asset["url"]).status_code == 404
    assert client.get(asset["url"], buffered=True).status_code == 200
    assert (
        client.delete(
            "/api/v1/admin/images/" + second.json["data"]["id"], json={"version": 1}, headers=auth
        ).status_code
        == 204
    )
    assert (
        client.delete(
            "/api/v1/admin/media/" + asset["id"], json={"version": 1}, headers=auth
        ).status_code
        == 204
    )
    assert not list(app.extensions["beront"].storage.uploads.iterdir())


def test_library_names_are_searchable_and_versioned(client, auth):
    asset = upload(client, auth).json["data"]
    response = client.patch(
        "/api/v1/admin/media/" + asset["id"],
        json={"version": 1, "name": "Nombre actualizado"},
        headers=auth,
    )
    assert response.status_code == 200 and response.json["data"]["version"] == 2
    assert (
        client.patch(
            "/api/v1/admin/media/" + asset["id"],
            json={"version": 1, "name": "Obsoleto"},
            headers=auth,
        ).status_code
        == 409
    )
    assert client.get("/api/v1/admin/media?q=actualizado").json["meta"]["total"] == 1
    assert client.get("/api/v1/admin/media?q=missing").json["data"] == []


def test_private_receipts_cannot_be_exposed_as_product_photos(client, auth, app, sample, database):
    product, _ = sample
    asset = upload(client, auth).json["data"]
    with database[2].begin() as connection:
        connection.execute(
            text("UPDATE media_assets SET kind='receipt' WHERE id=:id"), {"id": asset["id"]}
        )
    assert client.get("/api/v1/admin/media").json["data"] == []
    assert app.test_client().get(asset["url"]).status_code == 404
    response = client.post(
        "/api/v1/admin/products/" + str(product.id) + "/images",
        json={"asset_id": asset["id"]},
        headers=auth,
    )
    assert response.status_code == 422 and response.json["error"]["code"] == "INVALID_ASSET"


def test_library_requires_admin_permission_and_csrf(app, client, auth, monkeypatch):
    assert app.test_client().get("/api/v1/admin/media").status_code == 401
    assert (
        client.post("/api/v1/admin/media", data={"file": (photograph(), "x.png")}).status_code
        == 403
    )
    import beront.modules.identity.presentation.decorators as authorization

    monkeypatch.setattr(authorization, "PERMISSIONS", frozenset())
    assert client.get("/api/v1/admin/media").status_code == 403
