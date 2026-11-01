from decimal import Decimal
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import pytest
from sqlalchemy import text

from beront.modules.cart.infrastructure.whatsapp import WhatsAppLinkBuilder


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
