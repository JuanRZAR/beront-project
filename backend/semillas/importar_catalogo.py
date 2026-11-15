"""Importa la semilla sin reemplazar productos ni existencias ya registrados."""

import argparse
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from flask.cli import load_dotenv
from PIL import Image

from beront.app import create_app
from beront.modules.catalog.application.import_seed import ImportCatalogSeed
from beront.modules.catalog.presentation.schemas import (
    DefinitionCreate,
    ImageCreate,
    PresentationCreate,
    ProductCreate,
    VariantCreate,
)
from beront.modules.commerce.presentation.schemas import SettingsBody
from beront.modules.orders.presentation.schemas import StatusCreate

SOURCE = Path(__file__).resolve().parent / "catalogo"


def load_source(root=SOURCE):
    document = json.loads((root / "catalogo.json").read_text(encoding="utf-8"))
    if document.get("seed_version") != 2:
        raise ValueError("Versión de semilla no admitida.")
    SettingsBody.model_validate({"version": 0, **document["store_settings"]})
    for row in document["order_flow"]["statuses"]:
        StatusCreate.model_validate(row)
    slugs = {row["slug"] for row in document["order_flow"]["statuses"]}
    if any(
        row["from"] not in slugs or row["to"] not in slugs
        for row in document["order_flow"]["transitions"]
    ):
        raise ValueError("La semilla contiene una transición con estados inexistentes.")
    if set(document["definitions"]) != {"categories", "audiences", "presentations"}:
        raise ValueError("Los catálogos de configuración están incompletos.")
    for resource, rows in document["definitions"].items():
        schema = PresentationCreate if resource == "presentations" else DefinitionCreate
        for row in rows:
            schema.model_validate(row)
    filenames = set()
    for row in document["images"]:
        filename = row["file"]
        if not re.fullmatch(r"[a-f0-9]{32}\.webp", filename):
            raise ValueError("Nombre de fotografía no permitido.")
        path = (root / "imagenes" / filename).resolve()
        if path.parent != (root / "imagenes").resolve() or not path.is_file():
            raise ValueError("Falta una fotografía de la semilla.")
        if filename in filenames:
            raise ValueError("La semilla contiene fotografías duplicadas.")
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != row["sha256"]:
            raise ValueError("La fotografía no coincide con la semilla aprobada: " + filename)
        if len(payload) != row["size_bytes"]:
            raise ValueError("El tamaño de la fotografía no coincide con la semilla.")
        with Image.open(path) as image:
            if image.format != "WEBP" or image.size != (row["width"], row["height"]):
                raise ValueError("El formato o las dimensiones de la fotografía no coinciden.")
            if "A" not in image.getbands() or image.getchannel("A").getextrema()[0] == 255:
                raise ValueError("La fotografía debe conservar su transparencia.")
        filenames.add(filename)
    if {path.name for path in (root / "imagenes").iterdir() if path.is_file()} != filenames:
        raise ValueError("La carpeta de imágenes no coincide con el catálogo de la semilla.")
    brands = {}
    identifiers = set()
    referenced_images = set()
    categories = {row["slug"] for row in document["definitions"]["categories"]}
    audiences = {row["slug"] for row in document["definitions"]["audiences"]}
    presentations = {
        (row["kind"], Decimal(row["volume_ml"])) for row in document["definitions"]["presentations"]
    }
    for row in document["products"]:
        identifier = UUID(row["id"])
        if identifier in identifiers:
            raise ValueError("La semilla contiene perfumes duplicados.")
        identifiers.add(identifier)
        if len(row["classifications"]) != 1:
            raise ValueError("Cada marca debe tener una categoría.")
        name = row["brand"]["name"].casefold()
        category = row["classifications"][0]
        if category not in categories or row["audience"] not in audiences:
            raise ValueError("La semilla referencia una categoría o público no configurado.")
        if brands.setdefault(name, category) != category:
            raise ValueError("Una marca tiene categorías incompatibles.")
        ProductCreate.model_validate(
            {
                "brand_id": row["brand"]["id"],
                "name": row["name"],
                "slug": row["slug"],
                "audience": row["audience"],
            }
        )
        for variant in row["variants"]:
            UUID(variant["id"])
            VariantCreate.model_validate(
                {k: variant[k] for k in ("kind", "volume_ml", "price", "active", "sold_out")}
            )
            if (variant["kind"], Decimal(variant["volume_ml"])) not in presentations:
                raise ValueError("Falta una presentación en la configuración de la semilla.")
        if len(row["images"]) > 5:
            raise ValueError("Un perfume supera el límite de cinco imágenes.")
        for image in row["images"]:
            UUID(image["id"])
            if (
                not image["url"].startswith("/media/")
                or image["url"].rsplit("/", 1)[1] not in filenames
            ):
                raise ValueError("Referencia de fotografía no disponible localmente.")
            ImageCreate.model_validate({k: image[k] for k in ("position", "alt_es", "alt_en")})
            referenced_images.add(image["url"].rsplit("/", 1)[1])
    if referenced_images != filenames:
        raise ValueError("La semilla contiene fotografías sin un perfume asociado.")
    return document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Guardar en la base configurada en backend/.env."
    )
    args = parser.parse_args()
    document = load_source()
    print(
        f"Semilla válida: {len(document['products'])} perfumes y {len(document['images'])} imágenes."
    )
    if not args.apply:
        print(
            "Verificación sin conexión a BD. Usa --apply después de migrar y crear el administrador."
        )
        return
    load_dotenv(str(Path(__file__).resolve().parents[1] / ".env"))
    import_into(create_app(), document)


def import_into(app, document):
    services = app.extensions["beront"]
    importer = ImportCatalogSeed(services.uow_factory, services.media)
    result = importer.execute(
        document, lambda filename: (SOURCE / "imagenes" / filename).open("rb")
    )
    print(json.dumps(result, ensure_ascii=False))
    print(
        "Los nuevos saldos empiezan en cero. No se modificaron precios ni existencias anteriores."
    )


if __name__ == "__main__":
    main()
