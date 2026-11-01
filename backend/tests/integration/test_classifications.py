ROOT = "/api/v1/admin/catalog-options/"


def option(client, auth, resource, slug, es, en):
    response = client.post(
        ROOT + resource, json={"slug": slug, "name_es": es, "name_en": en}, headers=auth
    )
    assert response.status_code == 201, response.json
    return response.json["data"]


def test_options_are_configured_independently_per_dimension(app, client, auth):
    assert app.test_client().get(ROOT + "accords").status_code == 401
    option(client, auth, "accords", "amaderado", "Amaderado", "Woody")
    option(client, auth, "usages", "diario", "Diario", "Daily")
    option(client, auth, "profiles", "dulce", "Dulce", "Sweet")
    option(client, auth, "profiles", "citrico", "Cítrico", "Citrus")
    assert [r["slug"] for r in client.get(ROOT + "accords").json["data"]] == ["amaderado"]
    assert [r["slug"] for r in client.get(ROOT + "profiles").json["data"]] == ["citrico", "dulce"]
    duplicate = client.post(
        ROOT + "accords",
        json={"slug": "amaderado", "name_es": "Otro", "name_en": "Other"},
        headers=auth,
    )
    assert duplicate.status_code == 409
    option(client, auth, "usages", "amaderado", "Mismo slug, otra dimensión", "Same slug")
    facets = client.get("/api/v1/catalog/facets").json["data"]
    assert facets["accords"] == ["amaderado"] and facets["usages"] == ["diario", "amaderado"]
    assert facets["profiles"] == ["citrico", "dulce"]


def test_inactive_options_leave_public_facets_but_remain_editable(client, auth):
    created = option(client, auth, "accords", "vainilla", "Vainilla", "Vanilla")
    assert (
        client.patch(
            ROOT + "accords/" + created["id"],
            json={"version": 1, "active": False},
            headers=auth,
        ).status_code
        == 200
    )
    assert client.get("/api/v1/catalog/facets").json["data"]["accords"] == []
    assert [r["slug"] for r in client.get(ROOT + "accords").json["data"]] == ["vainilla"]


def test_products_carry_multiple_options_and_filter_by_them(client, auth, sample):
    product, _ = sample
    for resource, slug in (("accords", "amaderado"), ("accords", "ambar"), ("usages", "noche")):
        option(client, auth, resource, slug, slug, slug)
    option(client, auth, "profiles", "dulce", "Dulce", "Sweet")
    response = client.patch(
        "/api/v1/admin/products/" + str(product.id),
        json={
            "version": 2,
            "accords": ["amaderado", "ambar"],
            "usages": ["noche"],
            "profiles": [],
        },
        headers=auth,
    )
    assert response.status_code == 200, response.json
    data = response.json["data"]
    assert data["accords"] == ["amaderado", "ambar"] and data["usages"] == ["noche"]
    assert data["profiles"] == [] and data["version"] == 3
    public = "/api/v1/catalog/products"
    assert client.get(public + "?accord=amaderado").json["meta"]["total"] == 1
    assert client.get(public + "?accord=amaderado&accord=inexistente").json["meta"]["total"] == 1
    assert client.get(public + "?accord=amaderado&usage=noche").json["meta"]["total"] == 1
    assert client.get(public + "?accord=amaderado&profile=dulce").json["meta"]["total"] == 0
    assert client.get(public + "?usage=diario").json["meta"]["total"] == 0
    detail = client.get(public + "/" + product.slug).json["data"]
    assert detail["accords"] == ["amaderado", "ambar"]


def test_unknown_inactive_or_repeated_options_are_rejected(client, auth, sample):
    product, _ = sample
    created = option(client, auth, "accords", "fresco", "Fresco", "Fresh")
    path = "/api/v1/admin/products/" + str(product.id)
    unknown = client.patch(path, json={"version": 2, "accords": ["no-existe"]}, headers=auth)
    assert unknown.status_code == 422 and unknown.json["error"]["code"] == "INVALID_OPTION"
    repeated = client.patch(
        path, json={"version": 2, "accords": ["fresco", "fresco"]}, headers=auth
    )
    assert repeated.status_code == 422
    client.patch(
        ROOT + "accords/" + created["id"], json={"version": 1, "active": False}, headers=auth
    )
    inactive = client.patch(path, json={"version": 2, "accords": ["fresco"]}, headers=auth)
    assert inactive.status_code == 422 and inactive.json["error"]["code"] == "INVALID_OPTION"
    assert client.get(path).json["data"]["accords"] == []


def test_deactivated_option_is_hidden_from_products_and_filters(client, auth, sample):
    product, _ = sample
    created = option(client, auth, "profiles", "dulce", "Dulce", "Sweet")
    path = "/api/v1/admin/products/" + str(product.id)
    assert (
        client.patch(path, json={"version": 2, "profiles": ["dulce"]}, headers=auth).status_code
        == 200
    )
    client.patch(
        ROOT + "profiles/" + created["id"], json={"version": 1, "active": False}, headers=auth
    )
    assert client.get(path).json["data"]["profiles"] == []
    assert client.get("/api/v1/catalog/products?profile=dulce").json["meta"]["total"] == 0


def test_filters_reject_malformed_values(client):
    assert client.get("/api/v1/catalog/products?accord=NOT%20A%20SLUG").status_code == 422
