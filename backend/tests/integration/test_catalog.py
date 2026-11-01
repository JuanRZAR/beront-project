import io
from uuid import uuid4

import pytest
from PIL import Image


def test_public_filters_apply_to_same_variant(client, sample):
    product, variants = sample
    assert client.get("/api/v1/catalog/products?volume_ml=5&max_price=10").json["data"] == []
    response = client.get(
        "/api/v1/catalog/products?kind=decant&volume_ml=5&max_price=13&classification=niche"
    )
    assert response.status_code == 200
    data = response.json["data"][0]
    assert data["price_from"] == "12.50" and len(data["variants"]) == 1
    assert "version" not in data and "sold_out" not in data
    assert "amount" not in str(data)
    assert client.get("/api/v1/catalog/products?q=CASA").json["meta"]["total"] == 1
    assert client.get("/api/v1/catalog/products?q=%25").json["meta"]["total"] == 0
    assert (
        client.get("/api/v1/catalog/products?brand_id=" + str(product.brand_id)).json["meta"][
            "total"
        ]
        == 1
    )
    assert (
        client.get("/api/v1/catalog/products?audience=male&audience=unisex").json["meta"]["total"]
        == 1
    )


@pytest.mark.parametrize(
    "query",
    [
        "unknown=x",
        "max_price=1&min_price=2",
        "min_price=-1",
        "sort=DROP",
        "page=0",
        "page_size=49",
        "q=x&q=y",
        "volume_ml=0",
        "locale=fr",
    ],
)
def test_invalid_catalog_queries(client, query):
    assert client.get("/api/v1/catalog/products?" + query).status_code == 422


def test_public_detail_facets_and_locale(client, sample):
    product, _ = sample
    response = client.get("/api/v1/catalog/products/" + product.slug + "?locale=en")
    assert response.status_code == 200
    assert response.json["data"]["description_locale"] == "es"
    facets = client.get("/api/v1/catalog/facets").json["data"]
    assert facets["volumes_ml"] == ["5.00", "10.00", "100.00"]
    assert facets["brands"][0]["name"] == "Casa de prueba"
    assert client.get("/api/v1/catalog/products/missing").status_code == 404


def test_admin_product_workflow_and_versions(app, client, auth, reference_data):
    values = {"name": "Casa CRUD", "category_id": reference_data["id"]}
    response = client.post("/api/v1/admin/brands", json=values, headers=auth)
    assert response.status_code == 201
    brand = response.json["data"]
    assert (
        client.post(
            "/api/v1/admin/brands", json={**values, "name": "casa crud"}, headers=auth
        ).status_code
        == 409
    )
    product = client.post(
        "/api/v1/admin/products",
        json={
            "name": "Prueba CRUD",
            "brand_id": brand["id"],
            "slug": "prueba-crud",
            "audience": "female",
            "description_es": "Descripción.",
        },
        headers=auth,
    ).json["data"]
    path = "/api/v1/admin/products/" + product["id"]
    assert client.get("/api/v1/catalog/products/prueba-crud").status_code == 404
    assert (
        client.patch(path, json={"version": 1, "published": True}, headers=auth).status_code == 422
    )
    variant = client.post(
        path + "/variants",
        json={"kind": "decant", "volume_ml": "7.50", "price": "9.99"},
        headers=auth,
    )
    assert variant.status_code == 201
    variant_id = variant.json["data"]["id"]
    result = client.patch(
        path, json={"version": 1, "published": True, "description_en": "English."}, headers=auth
    )
    assert result.status_code == 200 and result.json["data"]["version"] == 2
    assert client.patch(path, json={"version": 1, "name": "Stale"}, headers=auth).status_code == 409
    assert (
        client.get("/api/v1/catalog/products/prueba-crud?locale=en").json["data"][
            "description_locale"
        ]
        == "en"
    )
    assert (
        client.patch(
            "/api/v1/admin/variants/" + variant_id,
            json={"version": 1, "volume_ml": "8"},
            headers=auth,
        ).status_code
        == 422
    )
    assert (
        client.patch(
            "/api/v1/admin/variants/" + variant_id,
            json={"version": 1, "price": "10.25"},
            headers=auth,
        ).status_code
        == 200
    )
    assert client.get(path).json["data"]["description_en"] == "English."
    assert client.get("/api/v1/admin/products").json["meta"]["total"] == 1
    assert (
        client.patch(path, json={"version": 2, "archived": True}, headers=auth).status_code == 200
    )
    assert client.get("/api/v1/catalog/products/prueba-crud").status_code == 404
    assert client.get("/api/v1/admin/brands").json["data"][0]["id"] == brand["id"]


def test_brand_update_hides_products(client, auth, sample):
    product, _ = sample
    path = "/api/v1/admin/brands/" + str(product.brand_id)
    response = client.patch(
        path, json={"version": 1, "active": False, "name": "Casa editada"}, headers=auth
    )
    assert response.status_code == 200
    assert client.get("/api/v1/catalog/products").json["data"] == []
    assert client.patch(path, json={"version": 1, "active": True}, headers=auth).status_code == 409


def test_out_of_stock_override_and_price_sorting(client, auth, sample):
    product, variants = sample
    path = "/api/v1/admin/products/" + str(product.id)
    assert (
        client.patch(path, json={"version": 2, "sold_out": True}, headers=auth).status_code == 200
    )
    assert client.get("/api/v1/catalog/products?available=true").json["data"] == []
    result = client.get("/api/v1/catalog/products?available=false&sort=price_desc").json["data"]
    assert len(result) == 1 and not result[0]["available"]
    assert (
        client.patch(path, json={"version": 3, "sold_out": False}, headers=auth).status_code == 200
    )
    assert client.get("/api/v1/catalog/products?sort=price_asc").json["data"][0]["available"]
    assert (
        client.patch(
            "/api/v1/admin/variants/" + str(variants[0].id),
            json={"version": 1, "sold_out": True},
            headers=auth,
        ).status_code
        == 200
    )
    result = client.get("/api/v1/catalog/products?kind=decant&available=true").json["data"][0]
    assert result["price_from"] == "20.00"


def image_payload(color="white"):
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), color).save(buffer, "PNG")
    buffer.seek(0)
    return buffer


def test_image_upload_visibility_edit_delete(app, client, auth, sample):
    product, _ = sample
    path = "/api/v1/admin/products/" + str(product.id)
    response = client.post(
        path + "/images",
        data={"file": (image_payload(), "../../test.png"), "alt_es": "Fotografía"},
        headers=auth,
    )
    assert response.status_code == 201, response.json
    image = response.json["data"]
    assert ".." not in image["url"]
    assert app.test_client().get(image["url"], buffered=True).status_code == 200
    edited = client.patch(
        "/api/v1/admin/images/" + image["id"],
        json={"version": 1, "alt_en": "Photograph", "position": 1},
        headers=auth,
    )
    assert edited.status_code == 200
    client.patch(path, json={"version": 2, "published": False}, headers=auth)
    assert app.test_client().get(image["url"]).status_code == 404
    assert client.get(image["url"], buffered=True).status_code == 200
    assert (
        client.delete(
            "/api/v1/admin/images/" + image["id"], json={"version": 1}, headers=auth
        ).status_code
        == 409
    )
    assert (
        client.delete(
            "/api/v1/admin/images/" + image["id"], json={"version": 2}, headers=auth
        ).status_code
        == 204
    )
    assert app.test_client().get(image["url"]).status_code == 404
    assert client.get(image["url"], buffered=True).status_code == 200
    assert len(list(app.extensions["beront"].storage.uploads.iterdir())) == 1


def test_image_limits_and_invalid_payloads(client, auth, sample):
    product, _ = sample
    path = "/api/v1/admin/products/" + str(product.id) + "/images"
    assert client.post(path, json={}, headers=auth).status_code == 422
    assert (
        client.post(path, data={"other": (image_payload(), "x.png")}, headers=auth).status_code
        == 422
    )
    assert (
        client.post(
            path, data={"file": (io.BytesIO(b"<svg></svg>"), "bad.png")}, headers=auth
        ).status_code
        == 422
    )
    for index in range(5):
        assert (
            client.post(
                path, data={"file": (image_payload((index * 30, 0, 0)), "x.png")}, headers=auth
            ).status_code
            == 201
        )
    assert (
        client.post(path, data={"file": (image_payload(), "x.png")}, headers=auth).status_code
        == 422
    )
    assert client.get("/media/not-a-generated-image").status_code == 404


def test_missing_entities_and_patch_validation(client, auth):
    missing = str(uuid4())
    assert client.get("/api/v1/admin/products/" + missing).status_code == 404
    assert (
        client.patch(
            "/api/v1/admin/products/" + missing, json={"version": 1}, headers=auth
        ).status_code
        == 422
    )
    assert (
        client.patch(
            "/api/v1/admin/products/" + missing, json={"version": 1, "name": None}, headers=auth
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/admin/products",
            json={
                "brand_id": missing,
                "name": "Missing",
                "slug": "missing",
                "audience": "male",
            },
            headers=auth,
        ).status_code
        == 404
    )


def test_image_rollback_removes_file(app, admin, sample, monkeypatch):
    product, _ = sample
    from beront.modules.catalog.infrastructure.repositories import SqlCatalogRepository

    def fail(*args):
        raise RuntimeError("Test failure")

    monkeypatch.setattr(SqlCatalogRepository, "add_image", fail)
    with pytest.raises(RuntimeError):
        app.extensions["beront"].catalog.add_image(product.id, image_payload(), {}, admin.id)
    assert not list(app.extensions["beront"].storage.uploads.iterdir())
