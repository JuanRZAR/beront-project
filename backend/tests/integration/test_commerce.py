import pytest


def test_settings_and_whatsapp_are_database_configuration(client, auth, sample, monkeypatch):
    monkeypatch.setenv("WHATSAPP_NUMBER", "not-used")
    assert client.get("/api/v1/admin/settings").json["data"] is None
    data = {
        "version": 0,
        "whatsapp_number": "593990000001",
        "terms_es": "Prueba",
        "terms_en": "Test",
    }
    assert client.put("/api/v1/admin/settings", json=data).status_code == 403
    result = client.put("/api/v1/admin/settings", json=data, headers=auth)
    assert result.status_code == 200
    assert client.put("/api/v1/admin/settings", json=data, headers=auth).status_code == 409
    _, variants = sample
    quote = client.post(
        "/api/v1/cart/quote", json={"items": [{"variant_id": str(variants[0].id), "quantity": 1}]}
    ).json["data"]
    assert quote["whatsapp_url"].startswith("https://wa.me/593990000001?")
    assert (
        client.put(
            "/api/v1/admin/settings",
            json={**data, "version": 1, "whatsapp_number": "593990000002"},
            headers=auth,
        ).status_code
        == 200
    )
    assert (
        client.get("/api/v1/checkout/options").json["data"]["settings"]["whatsapp_number"]
        == "593990000002"
    )


@pytest.mark.parametrize("number", ["invalid", "0123456789", "１２３４５６７８９"])
def test_invalid_commercial_phone(client, auth, number):
    assert (
        client.put(
            "/api/v1/admin/settings",
            json={"version": 0, "whatsapp_number": number, "terms_es": "", "terms_en": ""},
            headers=auth,
        ).status_code
        == 422
    )


def test_city_fee_and_island_exclusion(client, auth):
    root = "/api/v1/admin/commerce/"
    province = client.post(
        root + "provinces", json={"code": "17", "name": "Pichincha", "mainland": True}, headers=auth
    ).json["data"]
    island = client.post(
        root + "provinces",
        json={"code": "20", "name": "Galápagos", "mainland": False},
        headers=auth,
    ).json["data"]
    for parent, name, fee in [
        (province, "Quito", "5.25"),
        (province, "Cayambe", "7.50"),
        (island, "Santa Cruz", "9.00"),
    ]:
        assert (
            client.post(
                root + "cities",
                json={"province_id": parent["id"], "name": name, "shipping_fee": fee},
                headers=auth,
            ).status_code
            == 201
        )
    options = client.get("/api/v1/checkout/options").json["data"]
    assert [p["name"] for p in options["provinces"]] == ["Pichincha"]
    assert {c["name"]: c["shipping_fee"] for c in options["cities"]} == {
        "Quito": "5.25",
        "Cayambe": "7.50",
    }
    city = options["cities"][0]
    assert (
        client.patch(
            root + "cities/" + city["id"], json={"version": 1, "shipping_fee": "6.13"}, headers=auth
        ).status_code
        == 200
    )
    assert (
        client.patch(
            root + "cities/" + city["id"], json={"version": 1, "active": False}, headers=auth
        ).status_code
        == 409
    )
    assert (
        client.post(
            root + "provinces",
            json={"code": "20", "name": "Incorrecto", "mainland": True},
            headers=auth,
        ).status_code
        == 409
    )
