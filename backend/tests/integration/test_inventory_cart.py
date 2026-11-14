from dataclasses import replace
from decimal import Decimal
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import pytest
from sqlalchemy import text

from beront.app import create_app
from beront.modules.cart.infrastructure.whatsapp import WhatsAppLinkBuilder


@pytest.fixture
def open_stock_client(settings, sample, app, admin):
    product, variants = sample
    services = app.extensions["beront"]
    for kind, target, delta in (
        ("decant", product.id, "-20"),
        ("full_bottle", variants[2].id, "-2"),
    ):
        services.inventory.adjust(
            actor_id=admin.id,
            kind=kind,
            target_id=target,
            delta=Decimal(delta),
            version=2,
            reason="Retiro de existencias de prueba",
            operation_id=uuid4(),
        )
    services.commerce.save_settings(
        {"version": 0, "whatsapp_number": "593939237376", "terms_es": "", "terms_en": ""},
        admin.id,
    )
    application = create_app(replace(settings, cart_requires_stock=False))
    try:
        yield application.test_client()
    finally:
        application.extensions["beront"].engine.dispose()


def test_open_stock_cart_quotes_zero_balances_but_checkout_remains_strict(
    open_stock_client, client, sample, app
):
    product, variants = sample
    body = {"items": [{"variant_id": str(v.id), "quantity": 2} for v in variants]}
    assert client.post("/api/v1/cart/quote", json=body).status_code == 409
    quote = open_stock_client.post("/api/v1/cart/quote", json=body)
    assert quote.status_code == 200, quote.json
    assert quote.json["data"]["total"] == "305.00"
    summary = parse_qs(urlparse(quote.json["data"]["whatsapp_url"]).query)["text"][0]
    assert "Disponibilidad y envío por confirmar." in summary
    body["locale"] = "en"
    english = open_stock_client.post("/api/v1/cart/quote", json=body).json["data"]
    assert (
        "Availability and shipping to be confirmed."
        in parse_qs(urlparse(english["whatsapp_url"]).query)["text"][0]
    )
    detail = open_stock_client.get("/api/v1/catalog/products/" + product.slug).json["data"]
    assert all(v["available"] for v in detail["variants"])
    listing = open_stock_client.get("/api/v1/catalog/products?available=true").json
    assert listing["meta"]["total"] == 1
    checkout = open_stock_client.post(
        "/api/v1/checkout/quote", json={**body, "city_id": str(uuid4())}
    )
    assert checkout.status_code == 409
    assert checkout.json["error"]["code"] == "INSUFFICIENT_STOCK"
    services = app.extensions["beront"]
    with services.uow_factory() as uow:
        assert uow.stock.balance("decant", product.id).amount == 0
        assert uow.stock.balance("full_bottle", variants[2].id).amount == 0
        assert uow.stock.movements(1, 1)[1] == 4


@pytest.mark.parametrize("block", ["product_sold_out", "hidden", "variant_sold_out", "inactive"])
def test_open_stock_cart_still_blocks_unavailable_products(
    open_stock_client, app, admin, sample, block
):
    product, variants = sample
    catalog = app.extensions["beront"].catalog
    if block in {"product_sold_out", "hidden"}:
        catalog.update_product(
            product.id,
            {
                "version": product.version,
                "sold_out" if block == "product_sold_out" else "published": block != "hidden",
            },
            admin.id,
        )
    else:
        catalog.update_variant(
            variants[0].id,
            {
                "version": variants[0].version,
                "sold_out" if block == "variant_sold_out" else "active": block != "inactive",
            },
            admin.id,
        )
    response = open_stock_client.post(
        "/api/v1/cart/quote",
        json={"items": [{"variant_id": str(variants[0].id), "quantity": 1}]},
    )
    assert response.status_code == 409
    assert response.json["error"]["details"][0]["code"] == "UNAVAILABLE_PRODUCT"


def test_whatsapp_cart_summary_recalculates_quantities_and_removals_without_reserving_stock(
    app, client, admin, sample
):
    product, variants = sample
    services = app.extensions["beront"]
    services.commerce.save_settings(
        {"version": 0, "whatsapp_number": "593939237376", "terms_es": "", "terms_en": ""},
        admin.id,
    )
    with services.uow_factory() as uow:
        before = (
            uow.stock.balance("decant", product.id).amount,
            uow.stock.balance("full_bottle", variants[2].id).amount,
        )
        _, movements_before = uow.stock.movements(1, 1)

    def quote(decants, bottles):
        items = []
        for variant, quantity in ((variants[0], decants), (variants[2], bottles)):
            if quantity:
                items.append({"variant_id": str(variant.id), "quantity": quantity})
        response = client.post("/api/v1/cart/quote", json={"locale": "es", "items": items})
        assert response.status_code == 200, response.json
        return response.json["data"]

    combined = quote(2, 1)
    assert combined["total"] == "145.00"
    link = urlparse(combined["whatsapp_url"])
    assert link.scheme == "https" and link.netloc == "wa.me" and link.path == "/593939237376"
    summary = parse_qs(link.query)["text"][0]
    assert "Casa de prueba — Perfume de prueba" in summary
    assert "Decant" in summary and "Perfume completo" in summary
    assert (
        "*1. Casa de prueba — Perfume de prueba*\n"
        "Presentación: Decant · 5 ml\n"
        "Cantidad: 2\nPrecio unitario: USD 12.50\nSubtotal: USD 25.00\n\n"
        "*2. Casa de prueba — Perfume de prueba*\n"
        "Presentación: Perfume completo · 100 ml\n"
        "Cantidad: 1\nPrecio unitario: USD 120.00\nSubtotal: USD 120.00\n\n"
        "*Total: USD 145.00*\nNo incluye envío."
    ) in summary
    assert "Total: USD 145.00" in summary
    assert quote(1, 1)["total"] == "132.50"
    assert quote(1, 0)["total"] == "12.50"
    assert quote(0, 1)["total"] == "120.00"
    with services.uow_factory() as uow:
        assert (
            uow.stock.balance("decant", product.id).amount,
            uow.stock.balance("full_bottle", variants[2].id).amount,
        ) == before
        assert uow.stock.movements(1, 1)[1] == movements_before


def test_adjustment_idempotency_version_and_reasons(client, auth, sample):
    product, variants = sample
    body = {
        "kind": "decant",
        "target_id": str(product.id),
        "delta": "-5.50",
        "version": 2,
        "reason": "Venta de prueba",
        "operation_id": str(uuid4()),
    }
    path = "/api/v1/admin/inventory/adjustments"
    response = client.post(path, json=body, headers=auth)
    assert response.status_code == 201, response.json
    assert response.json["data"]["balance_after"] == "14.50"
    replay = client.post(path, json=body, headers=auth)
    assert replay.status_code == 200 and replay.json["data"] == response.json["data"]
    assert client.post(path, json={**body, "delta": "-1"}, headers=auth).status_code == 409
    assert (
        client.post(path, json={**body, "operation_id": str(uuid4())}, headers=auth).status_code
        == 409
    )
    assert (
        client.post(
            path,
            json={**body, "operation_id": str(uuid4()), "version": 3, "delta": "-20"},
            headers=auth,
        ).status_code
        == 422
    )
    assert (
        client.post(
            path,
            json={**body, "operation_id": str(uuid4()), "version": 3, "reason": " "},
            headers=auth,
        ).status_code
        == 422
    )
    listing = client.get("/api/v1/admin/inventory").json
    assert listing["meta"]["total"] == 2
    assert client.get("/api/v1/admin/inventory/movements").json["meta"]["total"] == 3
    assert len(client.get("/api/v1/admin/inventory?page_size=1&page=2").json["data"]) == 1
    assert client.get("/api/v1/admin/inventory?page_size=1&page=3").json["data"] == []


def test_inventory_lists_names_and_filters_server_side(client, auth, sample):
    product, variants = sample
    everything = client.get("/api/v1/admin/inventory", headers=auth).json
    assert [row["kind"] for row in everything["data"]] == ["decant", "full_bottle"]
    decant, bottle = everything["data"]
    assert decant["product_name"] == "Perfume de prueba"
    assert decant["brand_name"] == "Casa de prueba"
    assert decant["product_id"] == str(product.id) and decant["volume_ml"] is None
    assert bottle["target_id"] == str(variants[2].id) and bottle["volume_ml"] == "100.00"
    only_bottles = client.get("/api/v1/admin/inventory?kind=full_bottle").json
    assert [row["kind"] for row in only_bottles["data"]] == ["full_bottle"]
    assert only_bottles["meta"] == {"page": 1, "page_size": 24, "total": 1}
    assert client.get("/api/v1/admin/inventory?q=PRUEBA").json["meta"]["total"] == 2
    assert client.get("/api/v1/admin/inventory?q=casa de").json["meta"]["total"] == 2
    assert client.get("/api/v1/admin/inventory?q=inexistente").json["data"] == []
    assert client.get("/api/v1/admin/inventory?kind=otro").status_code == 422
    movement = client.get("/api/v1/admin/inventory/movements").json["data"][0]
    assert movement["product_name"] == "Perfume de prueba"
    assert movement["brand_name"] == "Casa de prueba"


def test_bottle_partial_sale_and_zero_stock(client, auth, sample):
    product, variants = sample
    response = client.post(
        "/api/v1/admin/inventory/adjustments",
        json={
            "kind": "full_bottle",
            "target_id": str(variants[2].id),
            "delta": "-2",
            "version": 2,
            "reason": "Botellas retiradas por venta externa",
            "operation_id": str(uuid4()),
        },
        headers=auth,
    )
    assert response.status_code == 201
    detail = client.get("/api/v1/catalog/products/" + product.slug).json["data"]
    assert not next(v for v in detail["variants"] if v["kind"] == "full_bottle")["available"]
    assert next(v for v in detail["variants"] if v["kind"] == "decant")["available"]


def test_inventory_transaction_rolls_back_all(app, admin, sample, monkeypatch):
    product, _ = sample
    from beront.shared.infrastructure.database import SqlUnitOfWork

    def fail(*args, **kwargs):
        raise RuntimeError("Audit failure")

    monkeypatch.setattr(SqlUnitOfWork, "audit", fail)
    operation_id = uuid4()
    with pytest.raises(RuntimeError):
        app.extensions["beront"].inventory.adjust(
            actor_id=admin.id,
            kind="decant",
            target_id=product.id,
            delta=Decimal("-5"),
            version=2,
            reason="Rollback test",
            operation_id=operation_id,
        )
    with app.extensions["beront"].uow_factory() as uow:
        assert uow.stock.balance("decant", product.id).amount == Decimal("20")
        assert uow.stock.movement(operation_id) is None


def test_quote_aggregate_stock_and_no_inventory_mutation(app, client, sample, database):
    product, variants = sample
    app.extensions["beront"].quote.whatsapp = WhatsAppLinkBuilder("00000000")

    def quote(first, second):
        return client.post(
            "/api/v1/cart/quote",
            json={
                "locale": "en",
                "items": [
                    {"variant_id": str(variants[0].id), "quantity": first},
                    {"variant_id": str(variants[1].id), "quantity": second},
                ],
            },
        )

    invalid = quote(3, 1)
    assert invalid.status_code == 409
    assert len(invalid.json["error"]["details"]) == 2
    valid = quote(2, 1)
    assert valid.status_code == 200, valid.json
    assert valid.json["data"]["total"] == "45.00"
    assert "USD 45.00" in parse_qs(urlparse(valid.json["data"]["whatsapp_url"]).query)["text"][0]
    with app.extensions["beront"].uow_factory() as uow:
        assert uow.stock.balance("decant", product.id).amount == Decimal("20")
    with database[2].connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM stock_movements")) == 2


def test_quote_reprices_and_missing_phone(client, auth, sample):
    product, variants = sample
    body = {"items": [{"variant_id": str(variants[0].id), "quantity": 1}]}
    first = client.post("/api/v1/cart/quote", json=body)
    assert first.json["data"]["total"] == "12.50"
    assert first.json["data"]["whatsapp_url"] is None
    assert first.json["data"]["configuration_error"] == "WHATSAPP_NOT_CONFIGURED"
    assert (
        client.patch(
            "/api/v1/admin/variants/" + str(variants[0].id),
            json={"version": 1, "price": "13.75"},
            headers=auth,
        ).status_code
        == 200
    )
    assert client.post("/api/v1/cart/quote", json=body).json["data"]["total"] == "13.75"
    assert client.post("/api/v1/cart/quote", json={**body, "total": "0.01"}).status_code == 422
    assert (
        client.post(
            "/api/v1/cart/quote", json={"items": [{**body["items"][0], "unit_price": "0.01"}]}
        ).status_code
        == 422
    )


def test_quote_lines_carry_product_link_image_and_sibling_options(client, sample):
    _, variants = sample
    body = {"items": [{"variant_id": str(variants[0].id), "quantity": 1}]}
    line = client.post("/api/v1/cart/quote", json=body).json["data"]["items"][0]
    assert line["product_slug"] == "perfume-prueba"
    assert line["image_url"] is None
    assert line["options"] == [
        {"variant_id": str(variants[0].id), "volume_ml": "5.00", "unit_price": "12.50"},
        {"variant_id": str(variants[1].id), "volume_ml": "10.00", "unit_price": "20.00"},
    ]


@pytest.mark.parametrize("quantity", [0, -1, True, 1.5, "2"])
def test_quote_invalid_quantities(client, quantity):
    assert (
        client.post(
            "/api/v1/cart/quote",
            json={"items": [{"variant_id": str(uuid4()), "quantity": quantity}]},
        ).status_code
        == 422
    )


def test_quote_hidden_missing_and_sold_out(client, auth, sample):
    product, variants = sample
    assert (
        client.post(
            "/api/v1/cart/quote", json={"items": [{"variant_id": str(uuid4()), "quantity": 1}]}
        ).status_code
        == 409
    )
    body = {"items": [{"variant_id": str(variants[0].id), "quantity": 1}]}
    client.patch(
        "/api/v1/admin/products/" + str(product.id),
        json={"version": 2, "sold_out": True},
        headers=auth,
    )
    assert client.post("/api/v1/cart/quote", json=body).status_code == 409
    assert (
        client.post(
            "/api/v1/cart/quote",
            json={"items": [{"variant_id": str(variants[0].id), "quantity": 11}] * 2},
        ).status_code
        == 422
    )
