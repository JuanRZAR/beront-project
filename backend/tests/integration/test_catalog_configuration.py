from decimal import Decimal

from sqlalchemy import text


def test_definitions_are_empty_until_admin_configures_them(client, auth):
    facets = client.get("/api/v1/catalog/facets").json["data"]
    assert facets["classifications"] == [] and facets["audiences"] == []
    assert facets["kinds"] == []
    path = "/api/v1/admin/catalog-options/categories"
    assert client.post(path, json={"slug": "test"}).status_code == 403
    created = client.post(
        path, json={"slug": "artesanal", "name_es": "Artesanal", "name_en": "Artisan"}, headers=auth
    )
    assert created.status_code == 201
    identifier = created.json["data"]["id"]
    assert client.get("/api/v1/catalog/facets").json["data"]["classifications"] == ["artesanal"]
    assert (
        client.patch(
            path + "/" + identifier, json={"version": 1, "name_es": "Autor"}, headers=auth
        ).status_code
        == 200
    )
    assert (
        client.patch(
            path + "/" + identifier, json={"version": 1, "active": False}, headers=auth
        ).status_code
        == 409
    )
    assert client.get("/api/v1/admin/catalog-options/anything").status_code == 404


def test_one_category_per_brand_and_dynamic_audience(client, auth, sample):
    product, _ = sample
    root = "/api/v1/admin/catalog-options/"
    category = client.post(
        root + "categories",
        json={"slug": "autor", "name_es": "Autor", "name_en": "Author"},
        headers=auth,
    ).json["data"]
    audience = client.post(
        root + "audiences",
        json={"slug": "nuevo-publico", "name_es": "Nuevo público", "name_en": "New audience"},
        headers=auth,
    ).json["data"]
    assert (
        client.patch(
            "/api/v1/admin/brands/" + str(product.brand_id),
            json={"version": 1, "category_id": category["id"]},
            headers=auth,
        ).status_code
        == 200
    )
    assert (
        client.patch(
            "/api/v1/admin/products/" + str(product.id),
            json={"version": 2, "audience": audience["slug"]},
            headers=auth,
        ).status_code
        == 200
    )
    data = client.get("/api/v1/catalog/products/" + product.slug).json["data"]
    assert data["classifications"] == ["autor"] and data["audience"] == "nuevo-publico"
    assert client.get("/api/v1/catalog/products?classification=niche").json["data"] == []
    assert (
        client.get("/api/v1/catalog/products?classification=autor&audience=nuevo-publico").json[
            "meta"
        ]["total"]
        == 1
    )
    assert (
        client.patch(
            root + "categories/" + category["id"],
            json={"version": 1, "active": False},
            headers=auth,
        ).status_code
        == 200
    )
    assert client.get("/api/v1/catalog/products/" + product.slug).status_code == 404


def test_variant_requires_configured_presentation_and_immutable_definition(
    client, auth, sample, database
):
    product, _ = sample
    path = "/api/v1/admin/products/" + str(product.id) + "/variants"
    data = {"kind": "decant", "volume_ml": "11.25", "price": "15.73"}
    assert client.post(path, json=data, headers=auth).status_code == 422
    root = "/api/v1/admin/catalog-options/presentations"
    definition = client.post(
        root,
        json={
            "kind": "decant",
            "volume_ml": "11.25",
            "name_es": "Personalizada",
            "name_en": "Custom",
        },
        headers=auth,
    ).json["data"]
    result = client.post(path, json=data, headers=auth)
    assert result.status_code == 201
    with database[2].connect() as connection:
        assert connection.scalar(
            text("SELECT price FROM variants WHERE id=:id"), {"id": result.json["data"]["id"]}
        ) == Decimal("15.73")
    assert (
        client.patch(
            root + "/" + definition["id"], json={"version": 1, "volume_ml": "15"}, headers=auth
        ).status_code
        == 422
    )
    assert (
        client.patch(
            root + "/" + definition["id"], json={"version": 1, "active": False}, headers=auth
        ).status_code
        == 409
    )
