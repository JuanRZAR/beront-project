from datetime import UTC, datetime, timedelta
from io import BytesIO
from uuid import uuid4

from PIL import Image

from beront.modules.commerce.application.seed_home import SeedHomeMessages

ROOT = "/api/v1/admin/home/messages"


def test_default_home_is_idempotent_and_does_not_publish_example(app, client, auth):
    seed = SeedHomeMessages(app.extensions["beront"].uow_factory)
    assert seed.execute() == 6
    assert len(client.get("/api/v1/home/messages").json["data"]) == 5
    rows = client.get(ROOT).json["data"]
    promotion = next(row for row in rows if row["slug"] == "promotion")
    assert not promotion["active"]
    row = rows[0]
    payload = {key: value for key, value in row.items() if key not in {"id", "images"}}
    payload["content"]["es"]["title"] = "Título del propietario"
    assert client.put(ROOT + "/" + row["id"], json=payload, headers=auth).status_code == 200
    assert seed.execute() == 0
    assert client.get(ROOT).json["data"][0]["content"]["es"]["title"] == "Título del propietario"


def message(**changes):
    text = {
        "eyebrow": "Inicio",
        "title": "Descubre",
        "emphasis": "tu perfume",
        "body": "Mensaje de prueba",
        "primary_label": "Ver decants",
        "secondary_label": "",
    }
    return {
        "slug": "message-" + uuid4().hex,
        "content": {"es": text, "en": {**text, "title": "Discover"}},
        "primary_path": "/catalog/decants",
        "active": True,
        **changes,
    }


def test_home_messages_require_auth_csrf_and_version(client, auth):
    anonymous = client.application.test_client()
    assert anonymous.get(ROOT).status_code == 401
    assert anonymous.get("/api/v1/home/messages").json == {"data": []}
    assert client.post(ROOT, json=message()).status_code == 403
    created = client.post(ROOT, json=message(), headers=auth)
    assert created.status_code == 201
    row = created.json["data"]
    assert row["version"] == 1 and row["images"] == []
    assert (
        client.get("/api/v1/home/messages").json["data"][0]["content"]["en"]["title"] == "Discover"
    )
    data = message(slug=row["slug"], version=1, active=False)
    assert client.put(ROOT + "/" + row["id"], json=data, headers=auth).status_code == 200
    assert client.put(ROOT + "/" + row["id"], json=data, headers=auth).status_code == 409
    assert client.get("/api/v1/home/messages").json["data"] == []
    assert len(client.get(ROOT).json["data"]) == 1


def test_home_messages_order_and_utc_schedule(client, auth):
    now = datetime.now(UTC)
    rows = [
        message(position=3),
        message(position=1),
        message(active=False),
        message(starts_at=(now + timedelta(days=1)).isoformat()),
        message(ends_at=(now - timedelta(days=1)).isoformat()),
    ]
    for row in rows:
        assert client.post(ROOT, json=row, headers=auth).status_code == 201
    visible = client.get("/api/v1/home/messages").json["data"]
    assert [row["position"] for row in visible] == [1, 3]
    assert len(client.get(ROOT).json["data"]) == 5
    for changes in (
        {"starts_at": now.replace(tzinfo=None).isoformat()},
        {"starts_at": now.isoformat(), "ends_at": now.isoformat()},
        {"primary_path": "javascript:alert(1)"},
        {"primary_path": "//example.com"},
        {"secondary_path": "/orders"},
    ):
        assert client.post(ROOT, json=message(**changes), headers=auth).status_code == 422


def test_home_assets_visibility_retention_and_atomic_update(client, auth, app, admin):
    stream = BytesIO()
    Image.new("RGBA", (12, 18), (110, 90, 30, 127)).save(stream, "PNG")
    stream.seek(0)
    asset, _ = app.extensions["beront"].media.upload(stream, "Frasco", admin.id)
    anonymous = app.test_client()
    assert anonymous.get(asset.url).status_code == 404
    payload = message(image_ids=[str(asset.id)])
    response = client.post(ROOT, json=payload, headers=auth)
    assert response.status_code == 201
    row = response.json["data"]
    assert row["images"][0]["url"] == asset.url
    with anonymous.get(asset.url, buffered=True) as photo:
        assert photo.status_code == 200
    assert (
        client.delete(
            "/api/v1/admin/media/" + str(asset.id), json={"version": 1}, headers=auth
        ).status_code
        == 409
    )
    assert (
        client.put(
            ROOT + "/" + row["id"],
            json={**payload, "version": 1, "image_ids": [str(uuid4())]},
            headers=auth,
        ).status_code
        == 422
    )
    assert client.get(ROOT).json["data"][0]["version"] == 1
    assert (
        client.post(ROOT, json=message(image_ids=[str(asset.id)] * 2), headers=auth).status_code
        == 422
    )
    assert (
        client.put(
            ROOT + "/" + row["id"], json={**payload, "version": 1, "active": False}, headers=auth
        ).status_code
        == 200
    )
    assert anonymous.get(asset.url).status_code == 404
    assert (
        client.put(
            ROOT + "/" + row["id"],
            json={**payload, "version": 2, "active": False, "image_ids": []},
            headers=auth,
        ).status_code
        == 200
    )
    assert (
        client.delete(
            "/api/v1/admin/media/" + str(asset.id), json={"version": 1}, headers=auth
        ).status_code
        == 204
    )


def test_home_rejects_receipts_as_public_art(app, client, auth, admin):
    services = app.extensions["beront"]
    with services.uow_factory() as uow:
        asset, _ = uow.media.register(
            {
                "filename": uuid4().hex + ".webp",
                "name": "Comprobante privado",
                "kind": "receipt",
                "checksum": None,
                "width": 1,
                "height": 1,
                "size_bytes": 1,
                "uploaded_by": admin.id,
            }
        )
        uow.commit()
    assert (
        client.post(ROOT, json=message(image_ids=[str(asset.id)]), headers=auth).status_code == 422
    )
    assert client.get("/api/v1/home/messages").json["data"] == []


def test_daily_home_uses_current_catalog_images_and_ecuador_day(
    app, client, auth, admin, reference_data
):
    from decimal import Decimal

    from beront.modules.catalog.application.import_photos import ImportCatalogPhotos

    services = app.extensions["beront"]
    catalog = services.catalog
    by_asset, products = {}, []
    categories = ("arabic", "designer", "niche")
    for category_index, category in enumerate(categories):
        definition = (
            reference_data
            if category == "niche"
            else catalog.create_definition(
                "categories", {"slug": category, "name_es": category, "name_en": category}, admin.id
            )
        )
        brand = catalog.create_brand(
            {"name": f"Fixture {category}", "category_id": definition["id"]}, admin.id
        )
        for index in range(2):
            product = catalog.create_product(
                {
                    "name": f"Fixture {category} {index}",
                    "slug": f"fixture-{category}-{index}",
                    "brand_id": brand.id,
                    "audience": "unisex",
                },
                admin.id,
            )
            catalog.create_variant(
                product.id,
                {"kind": "decant", "volume_ml": Decimal("5"), "price": Decimal("12")},
                admin.id,
            )
            stream = BytesIO()
            Image.new("RGBA", (12 + index, 20), (70 + category_index * 50, 90, 30, 127)).save(
                stream, "PNG"
            )
            stream.seek(0)
            photo = catalog.add_image(product.id, stream, {}, admin.id)
            by_asset[str(photo.asset_id)] = (product, category, photo)
            products.append((product, category))
            catalog.update_product(product.id, {"version": 1, "published": True}, admin.id)

    SeedHomeMessages(services.uow_factory).execute()
    saved = client.get(ROOT).json["data"]
    clock = [datetime(2026, 11, 13, 4, 59, tzinfo=UTC)]
    services.featured.now = lambda: clock[0]
    before = client.get("/api/v1/home/messages").json["data"]
    assert before == client.get("/api/v1/home/messages").json["data"]
    daily = {
        row["slug"]: row for row in before if row["slug"] in {"welcome", "decants", "full-bottles"}
    }
    assert len(daily) == 3
    for row in daily.values():
        assert [by_asset[image["id"]][1] for image in row["images"]] == list(categories)
        assert len(set(row["image_ids"])) == 3
        for image in row["images"]:
            with client.get(image["url"], buffered=True) as response:
                assert response.status_code == 200

    target = daily["welcome"]["images"][0]
    product, _, previous = by_asset[target["id"]]
    replacement = BytesIO()
    Image.new("RGBA", (80, 120), (30, 60, 200, 210)).save(replacement, "PNG")
    ImportCatalogPhotos(services.uow_factory, services.storage).execute(
        [
            {
                "product_id": product.id,
                "previous_image_id": previous.id,
                "image_id": uuid4(),
                "source": "fixture.png",
                "name": "Fixture",
            }
        ],
        lambda _: BytesIO(replacement.getvalue()),
    )
    refreshed = client.get("/api/v1/home/messages").json["data"]
    current = next(row for row in refreshed if row["slug"] == "welcome")["images"][0]
    assert current["url"] != target["url"] and current["name"] == target["name"]
    with client.get(current["url"], buffered=True) as response:
        assert response.status_code == 200
    clock[0] = datetime(2026, 11, 13, 5, 0, tzinfo=UTC)
    after = client.get("/api/v1/home/messages").json["data"]
    for row in after:
        if row["slug"] in daily:
            yesterday = next(item for item in refreshed if item["slug"] == row["slug"])
            assert all(
                a["name"] != b["name"]
                for a, b in zip(row["images"], yesterday["images"], strict=True)
            )
    assert client.get(ROOT).json["data"] == saved
    for product, category in products:
        if category == "niche":
            current_product = catalog.product(product.id)
            catalog.update_product(
                product.id, {"version": current_product.version, "published": False}, admin.id
            )
    visible = client.get("/api/v1/home/messages").json["data"]
    assert all(not row["images"] for row in visible if row["slug"] in daily)
