import io
import json
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier
from uuid import UUID, uuid4

import pytest
from PIL import Image
from sqlalchemy import text

from beront.modules.orders.presentation.schemas import OrderCreate


@pytest.fixture
def checkout(app, client, auth, sample, admin):
    services = app.extensions["beront"]
    actor = admin.id
    services.commerce.save_settings(
        {
            "version": 0,
            "whatsapp_number": "593990000001",
            "terms_es": "Términos de prueba",
            "terms_en": "Test terms",
        },
        actor,
    )
    province = services.commerce.create(
        "provinces", {"code": "17", "name": "Pichincha", "mainland": True}, actor
    )
    city = services.commerce.create(
        "cities",
        {"province_id": province["id"], "name": "Quito", "shipping_fee": Decimal("5.25")},
        actor,
    )
    bank = services.commerce.create(
        "banks",
        {
            "bank_name": "Banco de prueba",
            "account_type": "Cuenta de prueba",
            "account_number": "000123",
            "holder_name": "Titular de prueba",
            "holder_identification": "0000000000",
        },
        actor,
    )
    statuses = {}
    for slug, phase, purpose in [
        ("transfer", "awaiting_payment", "bank_transfer"),
        ("whatsapp", "awaiting_payment", "whatsapp"),
        ("issue", "stock_issue", "stock_issue"),
        ("paid", "paid", None),
        ("shipped", "shipped", None),
        ("delivered", "delivered", None),
        ("cancelled", "cancelled", None),
    ]:
        statuses[slug] = services.orders.create_definition(
            "statuses",
            {"slug": slug, "name_es": slug, "name_en": slug, "phase": phase, "purpose": purpose},
            actor,
        )
    for start, end in [
        ("transfer", "paid"),
        ("transfer", "issue"),
        ("transfer", "cancelled"),
        ("whatsapp", "paid"),
        ("whatsapp", "issue"),
        ("whatsapp", "cancelled"),
        ("issue", "paid"),
        ("issue", "cancelled"),
        ("paid", "shipped"),
        ("shipped", "delivered"),
        ("whatsapp", "shipped"),
    ]:
        services.orders.create_definition(
            "transitions",
            {"from_status_id": statuses[start]["id"], "to_status_id": statuses[end]["id"]},
            actor,
        )
    variant = sample[1][2]
    services.inventory.adjust(
        actor_id=actor,
        kind="full_bottle",
        target_id=variant.id,
        delta=Decimal("-1"),
        version=2,
        reason="Preparar última unidad",
        operation_id=uuid4(),
    )
    data = {
        "locale": "es",
        "items": [{"variant_id": str(variant.id), "quantity": 1}],
        "city_id": city["id"],
    }
    quote = client.post("/api/v1/checkout/quote", json=data)
    assert quote.status_code == 200, quote.json
    data.update(
        operation_id=str(uuid4()),
        quote_token=quote.json["data"]["quote_token"],
        customer={
            "cedula": "1712345678",
            "first_name": "Cliente",
            "last_name": "De prueba",
            "phone": "0991234567",
            "email": "cliente@example.test",
        },
        address="",
        payment_method="whatsapp",
        bank_id=None,
        terms_accepted=True,
    )
    return {
        "data": data,
        "statuses": statuses,
        "variant": variant,
        "actor": actor,
        "bank": bank,
        "city": city,
        "auth": auth,
    }


def photograph(color="white"):
    result = io.BytesIO()
    Image.new("RGB", (20, 20), color).save(result, "PNG")
    result.seek(0)
    return result


def create(client, checkout, *, transfer=False, operation=None):
    data = {**checkout["data"], "operation_id": operation or str(uuid4())}
    if transfer:
        data.update(payment_method="bank_transfer", bank_id=checkout["bank"]["id"])
        return client.post(
            "/api/v1/orders",
            data={"payload": json.dumps(data), "file": (photograph(), "receipt.png")},
            headers=checkout["auth"],
        ), data
    return client.post("/api/v1/orders", json=data, headers=checkout["auth"]), data


def private_id(client, code):
    return next(
        row["id"] for row in client.get("/api/v1/admin/orders").json["data"] if row["code"] == code
    )


def test_whatsapp_order_tracking_idempotency_and_unpaid_cancellation(client, checkout, database):
    response, data = create(client, checkout)
    assert response.status_code == 201, response.json
    order = response.json["data"]
    assert order["total"] == "125.25" and order["delivery_mode"] == "agency"
    assert order["payment_state"] == "pending" and "cedula" not in order and "receipts" not in order
    assert client.post("/api/v1/orders", json=data, headers=checkout["auth"]).status_code == 200
    assert (
        client.post(
            "/api/v1/orders", json={**data, "address": "Otra"}, headers=checkout["auth"]
        ).status_code
        == 409
    )
    with database[2].connect() as db:
        assert (
            db.scalar(
                text("SELECT amount FROM bottle_stock WHERE variant_id=:id"),
                {"id": checkout["variant"].id},
            )
            == 1
        )
        assert db.scalar(text("SELECT count(*) FROM orders")) == 1
    identifier = private_id(client, order["code"])
    reply = client.post(
        "/api/v1/admin/orders/" + identifier + "/transition",
        json={"version": 1, "status_id": checkout["statuses"]["cancelled"]["id"]},
        headers=checkout["auth"],
    )
    assert reply.status_code == 200, reply.json
    tracked = client.post("/api/v1/orders/track", json={"code": order["code"]})
    assert tracked.json["data"]["status"]["phase"] == "cancelled"
    assert tracked.headers["Cache-Control"] == "no-store"
    with database[2].connect() as db:
        assert (
            db.scalar(
                text("SELECT amount FROM bottle_stock WHERE variant_id=:id"),
                {"id": checkout["variant"].id},
            )
            == 1
        )


def test_bank_proof_is_required_private_and_can_be_corrected(app, client, checkout):
    data = {
        **checkout["data"],
        "payment_method": "bank_transfer",
        "bank_id": checkout["bank"]["id"],
    }
    assert client.post("/api/v1/orders", json=data, headers=checkout["auth"]).status_code == 422
    response, _ = create(client, checkout, transfer=True)
    assert response.status_code == 201, response.json
    identifier = private_id(client, response.json["data"]["code"])
    detail = client.get("/api/v1/admin/orders/" + identifier).json["data"]
    assert detail["payment_state"] == "pending" and len(detail["receipts"]) == 1
    proof = detail["receipts"][0]
    assert app.test_client().get(proof["url"]).status_code == 404
    with client.get(proof["url"], buffered=True) as image:
        assert image.status_code == 200
    corrected = client.post(
        "/api/v1/admin/orders/" + identifier + "/receipts",
        data={"file": (photograph("black"), "corrected.png")},
        headers=checkout["auth"],
    )
    assert corrected.status_code == 201 and len(corrected.json["data"]["receipts"]) == 2
    assert corrected.json["data"]["payment_state"] == "pending"


def test_payment_moves_inventory_once_then_shipping_and_tracking(client, checkout, database):
    response, _ = create(client, checkout)
    code = response.json["data"]["code"]
    identifier = private_id(client, code)
    root = "/api/v1/admin/orders/" + identifier
    assert (
        client.post(
            root + "/transition",
            json={"version": 1, "status_id": checkout["statuses"]["paid"]["id"]},
            headers=checkout["auth"],
        ).status_code
        == 409
    )
    assert (
        client.post(
            root + "/transition",
            json={
                "version": 1,
                "status_id": checkout["statuses"]["shipped"]["id"],
                "guide_number": "G1",
                "tracking_number": "T1",
            },
            headers=checkout["auth"],
        ).status_code
        == 409
    )
    data = {"version": 1, "status_id": checkout["statuses"]["paid"]["id"]}
    paid = client.post(root + "/approve-payment", json=data, headers=checkout["auth"])
    assert paid.status_code == 200, paid.json
    assert paid.json["payment_result"] == "confirmed"
    assert (
        client.post(root + "/approve-payment", json=data, headers=checkout["auth"]).json[
            "payment_result"
        ]
        == "already_confirmed"
    )
    assert (
        client.post(
            root + "/transition",
            json={"version": 2, "status_id": checkout["statuses"]["shipped"]["id"]},
            headers=checkout["auth"],
        ).status_code
        == 409
    )
    shipped = client.post(
        root + "/transition",
        json={
            "version": 2,
            "status_id": checkout["statuses"]["shipped"]["id"],
            "guide_number": "G1",
            "tracking_number": "T1",
        },
        headers=checkout["auth"],
    )
    assert shipped.status_code == 200, shipped.json
    tracked = client.post("/api/v1/orders/track", json={"code": code}).json["data"]
    assert tracked["guide_number"] == "G1" and tracked["tracking_number"] == "T1"
    assert tracked["status"]["phase"] == "shipped" and len(tracked["history"]) == 3
    with database[2].connect() as db:
        assert (
            db.scalar(
                text("SELECT amount FROM bottle_stock WHERE variant_id=:id"),
                {"id": checkout["variant"].id},
            )
            == 0
        )
        assert (
            db.scalar(
                text(
                    "SELECT count(*) FROM stock_movements WHERE delta=-1 AND reason LIKE 'Pedido %'"
                )
            )
            == 1
        )


def test_two_real_payments_for_last_unit_only_one_approval_consumes_stock(
    app, client, checkout, database
):
    identifiers = []
    for _ in range(2):
        response, _ = create(client, checkout, transfer=True)
        assert response.status_code == 201, response.json
        identifiers.append(UUID(private_id(client, response.json["data"]["code"])))
    ready = Barrier(2)

    def approve(identifier):
        ready.wait(timeout=10)
        return app.extensions["beront"].orders.approve_payment(
            identifier,
            {"version": 1, "status_id": UUID(checkout["statuses"]["paid"]["id"])},
            checkout["actor"],
        )[1]

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(approve, identifiers)) == ["confirmed", "stock_issue"]
    with database[2].connect() as db:
        assert (
            db.scalar(
                text("SELECT amount FROM bottle_stock WHERE variant_id=:id"),
                {"id": checkout["variant"].id},
            )
            == 0
        )
        assert db.scalar(text("SELECT count(*) FROM orders WHERE payment_state='confirmed'")) == 1
        assert db.scalar(text("SELECT count(*) FROM orders WHERE payment_state='stock_issue'")) == 1
        assert (
            db.scalar(text("SELECT count(*) FROM stock_movements WHERE reason LIKE 'Pedido %'"))
            == 1
        )


def recover(client, checkout, cedula, ip="203.0.113.10"):
    return client.post(
        "/api/v1/orders/recovery",
        json={"cedula": cedula},
        headers={**checkout["auth"], "X-Client-IP": ip},
    )


def test_recovery_emails_the_code_and_answers_uniformly(client, checkout, mailer):
    response, _ = create(client, checkout)
    code = response.json["data"]["code"]
    found = recover(client, checkout, "1712345678", "203.0.113.10")
    missing = recover(client, checkout, "0000000000", "203.0.113.11")
    assert found.status_code == missing.status_code == 202 and found.json == missing.json
    assert code not in str(found.json)
    assert [mail["to"] for mail in mailer.sent] == [checkout["data"]["customer"]["email"]]
    assert code in mailer.sent[0]["body"]
    assert "Estos son los códigos" in mailer.sent[0]["body"]
    assert client.get("/api/v1/admin/order-recoveries").status_code == 404


def test_recovery_cooldown_applies_per_identification_and_per_address(client, checkout, mailer):
    create(client, checkout)
    assert recover(client, checkout, "1712345678", "203.0.113.10").status_code == 202
    same_cedula = recover(client, checkout, "1712345678", "203.0.113.20")
    assert same_cedula.status_code == 429
    error = same_cedula.json["error"]
    assert error["code"] == "RECOVERY_COOLDOWN"
    assert 0 < error["details"][0]["seconds"] <= 600
    same_address = recover(client, checkout, "0000000000", "203.0.113.10")
    assert same_address.status_code == 429
    assert recover(client, checkout, "0000000000", "203.0.113.30").status_code == 202
    assert len(mailer.sent) == 1


def test_recovery_cooldown_expires_after_ten_minutes(client, checkout, mailer, database):
    create(client, checkout)
    assert recover(client, checkout, "1712345678").status_code == 202
    with database[2].begin() as db:
        db.execute(
            text(
                "UPDATE order_recovery_attempts SET created_at = created_at - interval '11 minutes'"
            )
        )
    assert recover(client, checkout, "1712345678").status_code == 202
    assert len(mailer.sent) == 2


def test_recovery_is_unavailable_without_mail_configuration(app, client, checkout):
    create(client, checkout)
    app.extensions["beront"].orders.mailer.configured = False
    response = recover(client, checkout, "1712345678")
    assert response.status_code == 503 and response.json["error"]["code"] == "RECOVERY_UNAVAILABLE"


def test_recovery_ignores_untrusted_forwarded_header_values(client, checkout):
    create(client, checkout)
    assert recover(client, checkout, "1712345678", "not-an-address").status_code == 202


def test_changed_quote_and_missing_csrf_cannot_create_order(client, checkout, database):
    data = checkout["data"]
    assert client.post("/api/v1/orders", json=data).status_code == 403
    assert (
        client.post(
            "/api/v1/orders",
            json={
                **data,
                "quote_token": data["quote_token"][:-1]
                + ("0" if data["quote_token"][-1] != "0" else "1"),
            },
            headers=checkout["auth"],
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/api/v1/orders", json={**data, "terms_accepted": False}, headers=checkout["auth"]
        ).status_code
        == 422
    )
    assert client.post("/api/v1/orders/track", json={"code": "BRT-" + "a" * 24}).status_code == 404
    with database[2].connect() as db:
        assert db.scalar(text("SELECT count(*) FROM orders")) == 0


def test_shared_decant_balance_and_bottles_are_all_or_nothing(
    app, client, checkout, sample, database
):
    services = app.extensions["beront"]
    product, variants = sample
    data = {
        **checkout["data"],
        "items": [
            {"variant_id": str(variants[0].id), "quantity": 2},
            {"variant_id": str(variants[1].id), "quantity": 1},
            {"variant_id": str(variants[2].id), "quantity": 1},
        ],
    }
    data["quote_token"] = client.post(
        "/api/v1/checkout/quote", json={k: data[k] for k in ("items", "city_id", "locale")}
    ).json["data"]["quote_token"]
    response = client.post("/api/v1/orders", json=data, headers=checkout["auth"])
    assert response.status_code == 201, response.json
    identifier = UUID(private_id(client, response.json["data"]["code"]))
    services.inventory.adjust(
        actor_id=checkout["actor"],
        kind="decant",
        target_id=product.id,
        delta=Decimal("-5"),
        version=2,
        reason="Venta manual anterior",
        operation_id=uuid4(),
    )
    approval = {"version": 1, "status_id": UUID(checkout["statuses"]["paid"]["id"])}
    order, result = services.orders.approve_payment(identifier, approval, checkout["actor"])
    assert result == "stock_issue"
    with database[2].connect() as db:
        assert (
            db.scalar(
                text("SELECT amount FROM bottle_stock WHERE variant_id=:id"), {"id": variants[2].id}
            )
            == 1
        )
        assert (
            db.scalar(
                text("SELECT amount FROM decant_stock WHERE product_id=:id"), {"id": product.id}
            )
            == 15
        )
        assert (
            db.scalar(text("SELECT count(*) FROM stock_movements WHERE reason LIKE 'Pedido %'"))
            == 0
        )
    assert (
        services.orders.approve_payment(
            identifier, {**approval, "version": order["version"]}, checkout["actor"]
        )[1]
        == "stock_issue"
    )
    services.inventory.adjust(
        actor_id=checkout["actor"],
        kind="decant",
        target_id=product.id,
        delta=Decimal("5"),
        version=3,
        reason="Reposición manual",
        operation_id=uuid4(),
    )
    assert (
        services.orders.approve_payment(
            identifier, {**approval, "version": order["version"]}, checkout["actor"]
        )[1]
        == "confirmed"
    )
    with database[2].connect() as db:
        assert (
            db.scalar(
                text("SELECT amount FROM bottle_stock WHERE variant_id=:id"), {"id": variants[2].id}
            )
            == 0
        )
        assert (
            db.scalar(
                text("SELECT amount FROM decant_stock WHERE product_id=:id"), {"id": product.id}
            )
            == 0
        )
        assert (
            db.scalar(text("SELECT count(*) FROM stock_movements WHERE reason LIKE 'Pedido %'"))
            == 2
        )


def test_failed_confirmation_rolls_back_every_inventory_write(
    app, client, checkout, database, monkeypatch
):
    from beront.modules.orders.infrastructure.repositories import SqlOrderRepository

    response, _ = create(client, checkout)
    identifier = UUID(private_id(client, response.json["data"]["code"]))

    def fail_save(*args):
        raise RuntimeError("Injected transaction failure")

    monkeypatch.setattr(SqlOrderRepository, "save", fail_save)
    with pytest.raises(RuntimeError):
        app.extensions["beront"].orders.approve_payment(
            identifier,
            {"version": 1, "status_id": UUID(checkout["statuses"]["paid"]["id"])},
            checkout["actor"],
        )
    with database[2].connect() as db:
        assert (
            db.scalar(
                text("SELECT amount FROM bottle_stock WHERE variant_id=:id"),
                {"id": checkout["variant"].id},
            )
            == 1
        )
        assert (
            db.scalar(text("SELECT payment_state FROM orders WHERE id=:id"), {"id": identifier})
            == "pending"
        )
        assert (
            db.scalar(text("SELECT count(*) FROM stock_movements WHERE reason LIKE 'Pedido %'"))
            == 0
        )


def test_concurrent_retries_create_one_order_and_debit_once(app, client, checkout, database):
    services = app.extensions["beront"]
    data = OrderCreate.model_validate(checkout["data"]).model_dump()
    ready = Barrier(2)

    def send(_):
        ready.wait(timeout=10)
        return services.orders.create(data)

    with ThreadPoolExecutor(max_workers=2) as pool:
        replies = list(pool.map(send, range(2)))
    assert sorted(created for _, created in replies) == [False, True]
    assert replies[0][0]["code"] == replies[1][0]["code"]
    identifier = UUID(replies[0][0]["id"])
    ready = Barrier(2)

    def approve(_):
        ready.wait(timeout=10)
        return services.orders.approve_payment(
            identifier,
            {"version": 1, "status_id": UUID(checkout["statuses"]["paid"]["id"])},
            checkout["actor"],
        )[1]

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(approve, range(2))) == ["already_confirmed", "confirmed"]
    with database[2].connect() as db:
        assert db.scalar(text("SELECT count(*) FROM orders")) == 1
        assert (
            db.scalar(text("SELECT count(*) FROM stock_movements WHERE reason LIKE 'Pedido %'"))
            == 1
        )


def test_flow_labels_are_configurable_but_cannot_bypass_payment(client, checkout):
    root = "/api/v1/admin/order-flow/"
    paid = checkout["statuses"]["paid"]
    updated = client.patch(
        root + "statuses/" + paid["id"],
        json={"version": 1, "name_es": "Compra validada"},
        headers=checkout["auth"],
    )
    assert updated.status_code == 200 and updated.json["data"]["name_es"] == "Compra validada"
    assert (
        client.patch(
            root + "statuses/" + paid["id"],
            json={"version": 2, "phase": "awaiting_payment"},
            headers=checkout["auth"],
        ).status_code
        == 422
    )
    response, _ = create(client, checkout)
    identifier = private_id(client, response.json["data"]["code"])
    path = "/api/v1/admin/orders/" + identifier
    assert (
        client.post(
            path + "/transition",
            json={"version": 1, "status_id": paid["id"]},
            headers=checkout["auth"],
        ).status_code
        == 409
    )
    approved = client.post(
        path + "/approve-payment",
        json={"version": 1, "status_id": paid["id"]},
        headers=checkout["auth"],
    )
    assert approved.json["data"]["status"]["name_es"] == "Compra validada"
    updated = client.patch(
        path + "/shipping",
        json={"version": 2, "guide_number": "Guía válida", "tracking_number": "SV-123"},
        headers=checkout["auth"],
    )
    assert updated.status_code == 200


def test_old_pending_order_does_not_expire(app, client, checkout, database):
    response, _ = create(client, checkout)
    identifier = UUID(private_id(client, response.json["data"]["code"]))
    with database[2].begin() as db:
        db.execute(
            text("UPDATE orders SET created_at=CURRENT_TIMESTAMP-INTERVAL '90 days' WHERE id=:id"),
            {"id": identifier},
        )
    assert (
        app.extensions["beront"].orders.approve_payment(
            identifier,
            {"version": 1, "status_id": UUID(checkout["statuses"]["paid"]["id"])},
            checkout["actor"],
        )[1]
        == "confirmed"
    )


def test_forged_transfer_cancelled_without_stock_change_and_bad_proof_leaves_no_file(
    app, client, checkout, database
):
    data = {
        **checkout["data"],
        "payment_method": "bank_transfer",
        "bank_id": checkout["bank"]["id"],
    }
    storage = app.extensions["beront"].storage
    before = set(storage.uploads.iterdir())
    response = client.post(
        "/api/v1/orders",
        data={"payload": json.dumps(data), "file": (io.BytesIO(b"<svg></svg>"), "receipt.png")},
        headers=checkout["auth"],
    )
    assert response.status_code == 422 and set(storage.uploads.iterdir()) == before
    response, _ = create(client, checkout, transfer=True)
    identifier = private_id(client, response.json["data"]["code"])
    assert (
        client.post(
            "/api/v1/admin/orders/" + identifier + "/transition",
            json={"version": 1, "status_id": checkout["statuses"]["cancelled"]["id"]},
            headers=checkout["auth"],
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/admin/orders/" + identifier + "/approve-payment",
            json={"version": 2, "status_id": checkout["statuses"]["paid"]["id"]},
            headers=checkout["auth"],
        ).status_code
        == 409
    )
    with database[2].connect() as db:
        assert (
            db.scalar(
                text("SELECT amount FROM bottle_stock WHERE variant_id=:id"),
                {"id": checkout["variant"].id},
            )
            == 1
        )


def test_disabled_or_relabelled_states_cannot_bypass_payment(client, checkout):
    response, _ = create(client, checkout)
    identifier = private_id(client, response.json["data"]["code"])
    root = "/api/v1/admin/orders/" + identifier
    statuses = checkout["statuses"]
    assert (
        client.post(
            root + "/transition",
            json={"version": 1, "status_id": statuses["issue"]["id"]},
            headers=checkout["auth"],
        ).status_code
        == 409
    )
    state_path = "/api/v1/admin/order-flow/statuses/" + statuses["paid"]["id"]
    assert (
        client.patch(
            state_path, json={"version": 1, "active": False}, headers=checkout["auth"]
        ).status_code
        == 200
    )
    assert (
        client.post(
            root + "/transition",
            json={"version": 1, "status_id": statuses["paid"]["id"]},
            headers=checkout["auth"],
        ).status_code
        == 409
    )
    assert (
        client.patch(
            state_path, json={"version": 2, "active": True}, headers=checkout["auth"]
        ).status_code
        == 200
    )
    assert (
        client.post(
            root + "/approve-payment",
            json={"version": 1, "status_id": statuses["paid"]["id"]},
            headers=checkout["auth"],
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/admin/order-flow/transitions",
            json={
                "from_status_id": statuses["paid"]["id"],
                "to_status_id": statuses["cancelled"]["id"],
            },
            headers=checkout["auth"],
        ).status_code
        == 201
    )
    assert (
        client.post(
            root + "/transition",
            json={"version": 2, "status_id": statuses["cancelled"]["id"]},
            headers=checkout["auth"],
        ).status_code
        == 409
    )
    corrected = client.post(
        root + "/receipts",
        data={"file": (photograph("blue"), "corrected.png")},
        headers=checkout["auth"],
    )
    assert corrected.status_code == 201 and corrected.json["data"]["payment_state"] == "confirmed"


def test_checkout_configuration_and_availability_fail_closed(app, client, checkout, database):
    services = app.extensions["beront"]
    settings = services.commerce.settings()
    services.commerce.save_settings({**settings, "whatsapp_number": ""}, checkout["actor"])
    data = dict(checkout["data"])
    data["quote_token"] = client.post(
        "/api/v1/checkout/quote", json={k: data[k] for k in ("items", "city_id", "locale")}
    ).json["data"]["quote_token"]
    assert (
        client.post("/api/v1/orders", json=data, headers=checkout["auth"]).json["error"]["code"]
        == "WHATSAPP_NOT_CONFIGURED"
    )
    assert (
        client.patch(
            "/api/v1/admin/commerce/banks/" + checkout["bank"]["id"],
            json={"version": 1, "active": False},
            headers=checkout["auth"],
        ).status_code
        == 200
    )
    data.update(payment_method="bank_transfer", bank_id=checkout["bank"]["id"])
    data["quote_token"] = client.post(
        "/api/v1/checkout/quote", json={k: data[k] for k in ("items", "city_id", "locale")}
    ).json["data"]["quote_token"]
    before = set(services.storage.uploads.iterdir())
    response = client.post(
        "/api/v1/orders",
        data={"payload": json.dumps(data), "file": (photograph(), "receipt.png")},
        headers=checkout["auth"],
    )
    assert response.status_code == 409 and response.json["error"]["code"] == "BANK_UNAVAILABLE"
    assert set(services.storage.uploads.iterdir()) == before
    services.commerce.save_settings(
        {**services.commerce.settings(), "terms_es": ""}, checkout["actor"]
    )
    quote_data = {k: data[k] for k in ("items", "city_id", "locale")}
    assert (
        client.post("/api/v1/checkout/quote", json=quote_data).json["error"]["code"]
        == "CHECKOUT_NOT_CONFIGURED"
    )
    services.inventory.adjust(
        actor_id=checkout["actor"],
        kind="full_bottle",
        target_id=checkout["variant"].id,
        delta=Decimal("-1"),
        version=3,
        reason="Última unidad vendida",
        operation_id=uuid4(),
    )
    assert client.post("/api/v1/checkout/quote", json=quote_data).status_code == 409
    with database[2].connect() as db:
        assert db.scalar(text("SELECT count(*) FROM orders")) == 0


def test_transfer_already_sent_can_be_registered_after_stock_and_prices_change(
    app, client, checkout, database
):
    services = app.extensions["beront"]
    first, _ = create(client, checkout)
    first_id = UUID(private_id(client, first.json["data"]["code"]))
    approval = {"version": 1, "status_id": UUID(checkout["statuses"]["paid"]["id"])}
    assert services.orders.approve_payment(first_id, approval, checkout["actor"])[1] == "confirmed"
    services.catalog.update_variant(
        checkout["variant"].id, {"version": 1, "price": Decimal("130")}, checkout["actor"]
    )
    services.commerce.update(
        "cities",
        UUID(checkout["city"]["id"]),
        {"version": 1, "shipping_fee": Decimal("9.75")},
        checkout["actor"],
    )
    services.commerce.update(
        "banks",
        UUID(checkout["bank"]["id"]),
        {"version": 1, "account_number": "999", "active": False},
        checkout["actor"],
    )
    services.commerce.save_settings(
        {**services.commerce.settings(), "terms_es": "Texto actualizado"}, checkout["actor"]
    )
    second, _ = create(client, checkout, transfer=True)
    assert second.status_code == 201, second.json
    assert second.json["data"]["total"] == "125.25"
    second_id = UUID(private_id(client, second.json["data"]["code"]))
    detail = services.orders.get(second_id)
    assert detail["bank_snapshot"]["account_number"] == "000123"
    assert detail["terms_snapshot"]["text"] == "Términos de prueba"
    assert (
        services.orders.approve_payment(second_id, approval, checkout["actor"])[1] == "stock_issue"
    )
    with database[2].connect() as db:
        assert db.scalar(text("SELECT count(*) FROM orders")) == 2
        assert (
            db.scalar(
                text("SELECT amount FROM bottle_stock WHERE variant_id=:id"),
                {"id": checkout["variant"].id},
            )
            == 0
        )


def test_signed_quote_cannot_be_reused_for_different_items_or_destination(client, checkout):
    data = checkout["data"]
    for changed in [
        {"city_id": str(uuid4())},
        {"items": [{"variant_id": str(checkout["variant"].id), "quantity": 2}]},
    ]:
        assert (
            client.post(
                "/api/v1/orders", json={**data, **changed}, headers=checkout["auth"]
            ).status_code
            == 409
        )
