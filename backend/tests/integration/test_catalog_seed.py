import importlib.util
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text

from beront.modules.catalog.application.import_seed import ImportCatalogSeed
from beront.shared.domain.errors import DomainError


def seed_module():
    path = Path(__file__).resolve().parents[2] / "semillas/importar_catalogo.py"
    spec = importlib.util.spec_from_file_location("catalog_seed", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_seed_requires_owner_before_writing_catalog(app):
    services = app.extensions["beront"]
    with pytest.raises(DomainError, match="Crea primero"):
        ImportCatalogSeed(services.uow_factory, services.media).execute({}, None)


def test_complete_seed_has_zero_stock_persisted_images_and_preserves_admin_changes(
    app, admin, database
):
    module = seed_module()
    document = module.load_source()
    services = app.extensions["beront"]
    importer = ImportCatalogSeed(services.uow_factory, services.media)

    def open_image(filename):
        return (module.SOURCE / "imagenes" / filename).open("rb")

    result = importer.execute(document, open_image)
    assert result["imported"] == 130 and result["skipped"] == 0
    with database[2].connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM products")) == 130
        assert connection.scalar(text("SELECT count(*) FROM variants")) == 400
        assert connection.scalar(text("SELECT count(*) FROM decant_stock WHERE amount<>0")) == 0
        assert connection.scalar(text("SELECT count(*) FROM bottle_stock WHERE amount<>0")) == 0
        assert (
            connection.scalar(
                text("SELECT count(*) FROM media_assets WHERE url NOT LIKE '/media/%'")
            )
            == 0
        )
        assert connection.scalar(text("SELECT count(*) FROM product_images")) == 135
    identifier = UUID(document["products"][0]["id"])
    product = services.catalog.product(identifier)
    variant = product.variants[0]
    services.catalog.update_variant(variant.id, {"version": 1, "price": "87.43"}, admin.id)
    services.inventory.adjust(
        actor_id=admin.id,
        kind="full_bottle",
        target_id=variant.id,
        delta=Decimal("3"),
        version=1,
        reason="Stock asignado por dueño",
        operation_id=uuid4(),
    )
    result = importer.execute(document, open_image)
    assert result == {"imported": 0, "skipped": 130, "new_images": 0}
    with database[2].connect() as connection:
        assert (
            str(
                connection.scalar(
                    text("SELECT price FROM variants WHERE id=:id"), {"id": variant.id}
                )
            )
            == "87.43"
        )
        assert (
            connection.scalar(
                text("SELECT amount FROM bottle_stock WHERE variant_id=:id"), {"id": variant.id}
            )
            == 3
        )
    client = app.test_client()
    response = client.get("/api/v1/catalog/products/" + product.slug)
    assert response.status_code == 200
    image = response.json["data"]["images"][0]
    assert image["url"].startswith("/media/")
    with client.get(image["url"], buffered=True) as photograph:
        assert photograph.status_code == 200 and photograph.data
    assert all(
        not row["available"]
        for row in client.get("/api/v1/catalog/products?kind=decant").json["data"]
    )
