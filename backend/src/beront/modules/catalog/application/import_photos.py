from beront.modules.catalog.domain.entities import ProductImage
from beront.shared.domain.errors import DomainError


class ImportCatalogPhotos:
    def __init__(self, uow_factory, storage):
        self.uow_factory, self.storage = uow_factory, storage

    @staticmethod
    def _selection(uow, replacements, *, lock=False):
        products = {}
        for product_id in sorted({row["product_id"] for row in replacements}, key=str):
            products[product_id] = uow.catalog.product(product_id, lock=lock)
        pending, skipped = [], 0
        for row in replacements:
            product = products[row["product_id"]]
            images = {image.id: image for image in product.images}
            previous, current = images.get(row["previous_image_id"]), images.get(row["image_id"])
            if current is not None and previous is None:
                skipped += 1
            elif previous is not None and current is None:
                pending.append((row, previous))
            else:
                raise DomainError(
                    "CATALOG_PHOTO_CHANGED",
                    f"La fotografía de {product.slug} cambió; revisa sus vínculos antes de importar.",
                )
        return pending, skipped

    def execute(self, replacements, open_image, *, dry_run=False):
        with self.uow_factory() as uow:
            owner = uow.identity.single()
            if not owner or not owner.active:
                raise DomainError("ADMIN_REQUIRED", "Se necesita un administrador activo.")
            pending, skipped = self._selection(uow, replacements)
        result = {
            "images": len({row["source"] for row, _ in pending}),
            "products": len({row["product_id"] for row, _ in pending}),
            "replaced": len(pending),
            "skipped": skipped,
        }
        if dry_run or not pending:
            return result

        files, unused = {}, []
        names = {row["source"]: row["name"] for row, _ in pending}
        try:
            for source in sorted({row["source"] for row, _ in pending}):
                with open_image(source) as stream:
                    files[source] = self.storage.save(stream)
            with self.uow_factory() as uow:
                pending, skipped = self._selection(uow, replacements, lock=True)
                assets = {}
                for source, filename in files.items():
                    asset, created = uow.media.register(
                        {
                            **self.storage.describe(filename),
                            "name": names[source],
                            "kind": "product",
                            "uploaded_by": owner.id,
                        }
                    )
                    assets[source] = asset
                    if created:
                        uow.audit(owner.id, "media.upload", asset.id)
                    else:
                        unused.append(filename)
                for row, previous in pending:
                    asset = assets[row["source"]]
                    uow.catalog.delete_image(previous.id, previous.version)
                    uow.catalog.add_image(
                        ProductImage(
                            id=row["image_id"],
                            product_id=previous.product_id,
                            filename=asset.filename,
                            asset_id=asset.id,
                            url=asset.url,
                            position=previous.position,
                            alt_es=previous.alt_es,
                            alt_en=previous.alt_en,
                        )
                    )
                    uow.audit(owner.id, "catalog.image_replace", previous.id)
                uow.commit()
                result["replaced"], result["skipped"] = len(pending), skipped
        except Exception:
            for filename in files.values():
                self.storage.delete(filename)
            raise
        for filename in unused:
            self.storage.delete(filename)
        return result
