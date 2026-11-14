from hashlib import sha256
from io import BytesIO
from uuid import uuid4

import pytest
from PIL import Image

from beront.modules.catalog.application.import_photos import ImportCatalogPhotos
from beront.modules.catalog.infrastructure.repositories import SqlCatalogRepository
from beront.shared.domain.errors import DomainError


def image_stream(*, transparent=False):
    image = Image.new("RGBA" if transparent else "RGB", (12, 18), "#426789")
    if transparent:
        image.putpixel((0, 0), (31, 85, 162, 0))
        image.putpixel((1, 1), (192, 163, 98, 127))
    stream = BytesIO()
    image.save(stream, "PNG")
    stream.seek(0)
    return stream


def prepare(app, admin, product):
    services = app.extensions["beront"]
    previous = services.catalog.add_image(
        product.id,
        image_stream(),
        {"position": 3, "alt_es": "Frasco", "alt_en": "Bottle"},
        admin.id,
    )
    replacement = {
        "product_id": product.id,
        "previous_image_id": previous.id,
        "image_id": uuid4(),
        "source": "source.webp",
        "name": product.name,
    }
    service = ImportCatalogPhotos(services.uow_factory, services.storage)
    return services, service, previous, replacement


def test_approved_photos_are_atomic_idempotent_and_keep_originals(app, client, admin, sample):
    services, service, previous, replacement = prepare(app, admin, sample[0])
    original_path = services.storage.path(previous.filename)
    original_hash = sha256(original_path.read_bytes()).hexdigest()
    files_before = set(services.storage.uploads.iterdir())
    expected = {"images": 1, "products": 1, "replaced": 1, "skipped": 0}
    assert (
        service.execute([replacement], lambda _: image_stream(transparent=True), dry_run=True)
        == expected
    )
    assert set(services.storage.uploads.iterdir()) == files_before
    assert services.catalog.product(sample[0].id).images[0].id == previous.id

    assert service.execute([replacement], lambda _: image_stream(transparent=True)) == expected
    current = services.catalog.product(sample[0].id).images[0]
    assert current.id == replacement["image_id"]
    assert (current.position, current.alt_es, current.alt_en) == (3, "Frasco", "Bottle")
    assert (
        original_path.is_file() and sha256(original_path.read_bytes()).hexdigest() == original_hash
    )
    with client.get(current.url, buffered=True) as response:
        assert response.status_code == 200 and response.mimetype == "image/webp"
        with Image.open(BytesIO(response.data)) as image:
            expected_pixels = Image.open(image_stream(transparent=True)).convert("RGBA").tobytes()
            assert image.convert("RGBA").tobytes() == expected_pixels
    files_after = set(services.storage.uploads.iterdir())
    assert service.execute([replacement], lambda _: image_stream(transparent=True)) == {
        "images": 0,
        "products": 0,
        "replaced": 0,
        "skipped": 1,
    }
    assert set(services.storage.uploads.iterdir()) == files_after


def test_approved_photo_failure_restores_links_assets_and_files(app, admin, sample, monkeypatch):
    services, service, previous, replacement = prepare(app, admin, sample[0])
    before = set(services.storage.uploads.iterdir())

    def fail(*args):
        raise RuntimeError("forced database failure")

    monkeypatch.setattr(SqlCatalogRepository, "add_image", fail)
    with pytest.raises(RuntimeError):
        service.execute([replacement], lambda _: image_stream(transparent=True))
    assert services.catalog.product(sample[0].id).images[0].id == previous.id
    assert services.media.listing()[1] == 1
    assert set(services.storage.uploads.iterdir()) == before


def test_approved_photos_refuse_changed_catalog_bindings(app, admin, sample):
    services, service, previous, replacement = prepare(app, admin, sample[0])
    services.catalog.delete_image(previous.id, previous.version, admin.id)
    before = set(services.storage.uploads.iterdir())
    with pytest.raises(DomainError, match="cambió"):
        service.execute([replacement], lambda _: image_stream(transparent=True))
    assert set(services.storage.uploads.iterdir()) == before
