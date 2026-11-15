import hashlib
import json
from io import BytesIO
from uuid import uuid4

import pytest
from PIL import Image

from beront.modules.catalog.infrastructure.approved_images import load_approved_images


def test_current_seed_rejects_legacy_photo_replacement(tmp_path):
    with pytest.raises(ValueError, match="ya incluye las fotos sin fondo"):
        load_approved_images(tmp_path / "manifest.json", {"seed_version": 2}, tmp_path)


def test_approved_images_validate_sources_and_reject_changed_files(tmp_path):
    originals, approved = tmp_path / "originals", tmp_path / "approved"
    originals.mkdir()
    approved.mkdir()
    original = originals / "source.webp"
    Image.new("RGB", (6, 4), "#426789").save(original, "WEBP")
    source_bytes = original.read_bytes()
    png = approved / "inkscape-r02-001.png"
    Image.new("RGBA", (6, 4), (31, 85, 162, 127)).save(png, "PNG")
    png_bytes = png.read_bytes()
    manifest = approved / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "revision": "R02",
                "scope": "bottle only",
                "photos": {
                    "source.webp": {
                        "sha256": hashlib.sha256(source_bytes).hexdigest(),
                        "artifacts": {
                            "png": {
                                "file": png.name,
                                "sha256": hashlib.sha256(png_bytes).hexdigest(),
                            }
                        },
                    }
                },
            }
        )
    )
    document = {
        "products": [
            {
                "id": str(uuid4()),
                "brand": {"name": "Casa de prueba"},
                "name": "Perfume de prueba",
                "images": [{"id": str(uuid4()), "url": "/temporal/media/source.webp"}],
            }
        ]
    }
    rows, open_image = load_approved_images(manifest, document, originals)
    assert len(rows) == 1
    assert open_image("source.webp").getvalue() == png_bytes
    assert rows == load_approved_images(manifest, document, originals)[0]
    with Image.open(BytesIO(png_bytes)) as image:
        assert image.mode == "RGBA"
    png.write_bytes(png_bytes + b"changed")
    with pytest.raises(ValueError, match="no coincide"):
        load_approved_images(manifest, document, originals)
    png.write_bytes(png_bytes)
    original.write_bytes(b"changed")
    with pytest.raises(ValueError, match="original"):
        load_approved_images(manifest, document, originals)
    original.write_bytes(source_bytes)
    png.unlink()
    outside = tmp_path / "outside.png"
    outside.write_bytes(png_bytes)
    png.symlink_to(outside)
    with pytest.raises(ValueError, match="junto al manifiesto"):
        load_approved_images(manifest, document, originals)
