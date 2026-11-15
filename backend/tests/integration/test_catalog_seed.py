import hashlib
import importlib.util
import shutil
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text

from beront.modules.catalog.application.import_seed import ImportCatalogSeed
from beront.modules.commerce.application.seed_home import default_messages
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


def test_home_seed_only_references_canonical_products():
    slugs = {product["slug"] for product in seed_module().load_source()["products"]}
    assert all(set(message["products"]) <= slugs for message in default_messages())


def test_seed_rejects_changed_or_unlisted_photographs(tmp_path):
    module = seed_module()
    root = tmp_path / "catalogo"
    shutil.copytree(module.SOURCE, root)
    document = module.load_source(root)
    photograph = root / "imagenes" / document["images"][0]["file"]
    original = photograph.read_bytes()
    photograph.write_bytes(original + b"changed")
    with pytest.raises(ValueError, match="no coincide con la semilla aprobada"):
        module.load_source(root)
    photograph.write_bytes(original)
    (root / "imagenes" / ("0" * 32 + ".webp")).write_bytes(original)
    with pytest.raises(ValueError, match="carpeta de imágenes"):
        module.load_source(root)


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
    assert result == {"imported": 127, "skipped": 0, "new_images": 133}
    with database[2].connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM products")) == 127
        assert connection.scalar(text("SELECT count(*) FROM variants")) == 425
        assert connection.scalar(text("SELECT count(*) FROM brands")) == 43
        assert connection.scalar(text("SELECT count(*) FROM variants WHERE NOT active")) == 9
        assert connection.scalar(text("SELECT count(*) FROM decant_stock WHERE amount<>0")) == 0
        assert connection.scalar(text("SELECT count(*) FROM bottle_stock WHERE amount<>0")) == 0
        assert (
            connection.scalar(
                text("SELECT count(*) FROM media_assets WHERE url NOT LIKE '/media/%'")
            )
            == 0
        )
        assert connection.scalar(text("SELECT count(*) FROM product_images")) == 133
    client = app.test_client()
    source_images = {image["file"]: image for image in document["images"]}
    for source in document["products"]:
        product = services.catalog.product(UUID(source["id"]))
        assert (product.name, product.slug, product.brand_name) == (
            source["name"],
            source["slug"],
            source["brand"]["name"],
        )
        variants = {variant.id: variant for variant in product.variants}
        for expected in source["variants"]:
            actual = variants[UUID(expected["id"])]
            assert (
                actual.kind,
                actual.volume_ml,
                actual.price,
                actual.active,
                actual.sold_out,
            ) == (
                expected["kind"],
                Decimal(expected["volume_ml"]),
                Decimal(expected["price"]),
                expected["active"],
                expected["sold_out"],
            )
        for actual, expected in zip(product.images, source["images"], strict=True):
            assert (actual.position, actual.alt_es, actual.alt_en) == (
                expected["position"],
                expected["alt_es"],
                expected["alt_en"],
            )
            photograph = client.get(actual.url, buffered=True)
            assert photograph.status_code == 200
            filename = expected["url"].rsplit("/", 1)[1]
            assert hashlib.sha256(photograph.data).hexdigest() == source_images[filename]["sha256"]
    assert client.get("/api/v1/catalog/products?kind=decant").json["meta"]["total"] == 127
    identifier = UUID(
        next(
            row["id"]
            for row in document["products"]
            if any(
                variant["kind"] == "full_bottle" and variant["active"]
                for variant in row["variants"]
            )
        )
    )
    product = services.catalog.product(identifier)
    variant = next(row for row in product.variants if row.kind == "full_bottle" and row.active)
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
    assert result == {"imported": 0, "skipped": 127, "new_images": 0}
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
