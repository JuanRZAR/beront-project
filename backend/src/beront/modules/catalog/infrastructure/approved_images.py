import hashlib
import json
import re
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5


def load_approved_images(manifest_path, document, originals):
    manifest_path = Path(manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("revision") != "R02" or manifest.get("scope") != "bottle only":
        raise ValueError("Se necesita el manifiesto aprobado Inkscape R02, solo frascos.")
    photos = manifest.get("photos", {})
    expected = {Path(image["url"]).name for row in document["products"] for image in row["images"]}
    if set(photos) != expected:
        raise ValueError("El manifiesto no cubre exactamente las fotografías del catálogo.")
    paths, checksums = {}, {}
    for source, photo in photos.items():
        original = Path(originals) / source
        if hashlib.sha256(original.read_bytes()).hexdigest() != photo["sha256"]:
            raise ValueError("Cambió una fotografía original: " + source)
        artifact = photo["artifacts"]["png"]
        filename = artifact["file"]
        if not re.fullmatch(r"inkscape-r02-[0-9]{3}\.png", filename):
            raise ValueError("Nombre de recorte no permitido.")
        path = (manifest_path.parent / filename).resolve()
        if path.parent != manifest_path.parent:
            raise ValueError("El recorte debe estar junto al manifiesto.")
        payload = path.read_bytes()
        if not payload.startswith(b"\x89PNG\r\n\x1a\n") or len(payload) > 5 * 1024 * 1024:
            raise ValueError("El recorte debe ser PNG y no superar 5 MiB: " + filename)
        checksum = hashlib.sha256(payload).hexdigest()
        if checksum != artifact["sha256"]:
            raise ValueError("El recorte no coincide con el aprobado: " + filename)
        paths[source], checksums[source] = path, checksum
    replacements = []
    for product in document["products"]:
        product_id = UUID(product["id"])
        for image in product["images"]:
            source = Path(image["url"]).name
            previous_id = uuid5(NAMESPACE_URL, f"beront:seed:image:{product_id}:{image['id']}")
            replacements.append(
                {
                    "product_id": product_id,
                    "previous_image_id": previous_id,
                    "image_id": uuid5(
                        NAMESPACE_URL, f"beront:inkscape:r02:{previous_id}:{checksums[source]}"
                    ),
                    "source": source,
                    "name": product["brand"]["name"] + " " + product["name"],
                }
            )

    def open_image(source):
        payload = paths[source].read_bytes()
        if hashlib.sha256(payload).hexdigest() != checksums[source]:
            raise ValueError("El recorte cambió durante la importación.")
        from io import BytesIO

        return BytesIO(payload)

    return replacements, open_image
