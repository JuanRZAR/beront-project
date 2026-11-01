from decimal import Decimal
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from beront.modules.catalog.domain.entities import Brand, Product, ProductImage, Variant
from beront.modules.catalog.domain.policies import ensure_publishable
from beront.shared.domain.errors import DomainError, NotFound


class ImportCatalogSeed:
    def __init__(self, uow_factory, media):
        self.uow_factory, self.media = uow_factory, media

    def execute(self, document, open_image):
        with self.uow_factory() as uow:
            owner = uow.identity.single()
            if not owner or not owner.active:
                raise DomainError(
                    "ADMIN_REQUIRED", "Crea primero el administrador con createsuperuser."
                )
        actor_id = owner.id
        with self.uow_factory() as uow:
            if not uow.commerce.settings():
                uow.commerce.save_settings({"version": 0, **document["store_settings"]})
            statuses = {row["slug"]: row for row in uow.orders.definitions("statuses")}
            purposes = {row["purpose"]: row for row in statuses.values() if row["purpose"]}
            for row in document["order_flow"]["statuses"]:
                if row["slug"] not in statuses:
                    statuses[row["slug"]] = purposes.get(
                        row.get("purpose")
                    ) or uow.orders.add_definition("statuses", {"id": uuid4(), **row})
            pairs = {
                (row["from_status_id"], row["to_status_id"])
                for row in uow.orders.definitions("transitions")
            }
            for row in document["order_flow"]["transitions"]:
                start, end = statuses[row["from"]]["id"], statuses[row["to"]]["id"]
                if (start, end) not in pairs:
                    uow.orders.add_definition(
                        "transitions", {"id": uuid4(), "from_status_id": start, "to_status_id": end}
                    )
            uow.audit(actor_id, "commerce.seed_check")
            uow.commit()
        definitions = {}
        for resource, rows in document["definitions"].items():
            with self.uow_factory() as uow:
                existing = uow.catalog.definitions(resource, private=True)
                key = self._definition_key
                indexed = {key(resource, row): row for row in existing}
                for row in rows:
                    identity = key(resource, row)
                    if identity not in indexed:
                        indexed[identity] = uow.catalog.add_definition(
                            resource, {"id": uuid4(), **row}
                        )
                definitions[resource] = indexed
                uow.commit()

        assets = {}
        created_assets = 0
        image_names = {
            image["url"].rsplit("/", 1)[1]: row["brand"]["name"] + " " + row["name"]
            for row in document["products"]
            for image in row["images"]
        }
        for source in document["images"]:
            with open_image(source["file"]) as stream:
                asset, created = self.media.upload(
                    stream, image_names.get(source["file"], source["file"]), actor_id
                )
            assets[source["file"]] = asset
            created_assets += int(created)

        with self.uow_factory() as uow:
            brands = {brand.name.casefold(): brand for brand in uow.catalog.brands(private=True)}
            for row in document["products"]:
                name = row["brand"]["name"]
                if name.casefold() not in brands:
                    category = definitions["categories"][row["classifications"][0]]
                    brand = Brand(UUID(row["brand"]["id"]), name, category_id=UUID(category["id"]))
                    uow.catalog.add_brand(brand)
                    brands[name.casefold()] = brand
            uow.commit()

        imported, skipped = 0, 0
        for row in document["products"]:
            with self.uow_factory() as uow:
                identifier = UUID(row["id"])
                try:
                    uow.catalog.product(identifier)
                except NotFound:
                    pass
                else:
                    skipped += 1
                    continue
                brand = brands[row["brand"]["name"].casefold()]
                product = Product(
                    id=identifier,
                    brand_id=brand.id,
                    name=row["name"],
                    slug=row["slug"],
                    audience=row["audience"],
                    classifications=[],
                    description_es=row.get("description_es", ""),
                    description_en=row.get("description_en", ""),
                )
                uow.catalog.add_product(product)
                uow.stock.ensure_decants(product.id)
                for source in row["variants"]:
                    variant = Variant(
                        UUID(source["id"]),
                        product.id,
                        source["kind"],
                        Decimal(source["volume_ml"]),
                        Decimal(source["price"]),
                    )
                    uow.catalog.add_variant(variant)
                    if variant.kind == "full_bottle":
                        uow.stock.ensure_bottles(variant.id)
                    product.variants.append(variant)
                for source in row["images"]:
                    asset = assets[source["url"].rsplit("/", 1)[1]]
                    uow.catalog.add_image(
                        ProductImage(
                            id=uuid5(
                                NAMESPACE_URL, f"beront:seed:image:{product.id}:{source['id']}"
                            ),
                            product_id=product.id,
                            asset_id=asset.id,
                            filename=asset.filename,
                            url=asset.url,
                            position=source["position"],
                            alt_es=source["alt_es"],
                            alt_en=source["alt_en"],
                        )
                    )
                product.published = True
                ensure_publishable(product)
                uow.catalog.save_product(product)
                uow.audit(actor_id, "catalog.seed_import", product.id)
                uow.commit()
                imported += 1
        return {"imported": imported, "skipped": skipped, "new_images": created_assets}

    @staticmethod
    def _definition_key(resource, row):
        if resource == "presentations":
            return row["kind"], Decimal(row["volume_ml"])
        return row["slug"]
