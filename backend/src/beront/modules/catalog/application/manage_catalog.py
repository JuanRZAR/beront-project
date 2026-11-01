from uuid import uuid4

from beront.modules.catalog.domain.entities import Brand, Product, ProductImage, Variant
from beront.modules.catalog.domain.policies import ensure_publishable, ensure_version
from beront.shared.domain.errors import DomainError, NotFound
from beront.shared.domain.values import decimal_value


class CatalogService:
    OPTIONS = ("accords", "usages", "profiles")
    DEFINITIONS = frozenset({"categories", "audiences", "presentations", *OPTIONS})

    def __init__(self, uow_factory, storage):
        self.uow_factory, self.storage = uow_factory, storage

    def brands(self, *, private=False):
        with self.uow_factory() as uow:
            return uow.catalog.brands(private=private)

    def definitions(self, resource, *, private=False):
        if resource not in self.DEFINITIONS:
            raise NotFound()
        with self.uow_factory() as uow:
            return uow.catalog.definitions(resource, private=private)

    def create_definition(self, resource, data, actor_id, request_id=None):
        if resource not in self.DEFINITIONS:
            raise NotFound()
        with self.uow_factory() as uow:
            result = uow.catalog.add_definition(resource, {"id": uuid4(), **data})
            uow.audit(actor_id, "catalog." + resource + "_create", result["id"], request_id)
            uow.commit()
            return result

    def update_definition(self, resource, identifier, data, actor_id, request_id=None):
        if resource not in self.DEFINITIONS:
            raise NotFound()
        with self.uow_factory() as uow:
            current = uow.catalog.definition(resource, identifier)
            if current["version"] != data["version"]:
                from beront.shared.domain.errors import Conflict

                raise Conflict()
            result = uow.catalog.save_definition(resource, {**current, **data})
            uow.audit(actor_id, "catalog." + resource + "_update", identifier, request_id)
            uow.commit()
            return result

    @staticmethod
    def _classification(repository, brand_id):
        brand = repository.brand(brand_id)
        return [repository.definition("categories", brand.category_id)["slug"]]

    def create_brand(self, data, actor_id, request_id=None):
        with self.uow_factory() as uow:
            uow.catalog.definition("categories", data["category_id"])
            brand = Brand(uuid4(), **data)
            uow.catalog.add_brand(brand)
            uow.audit(actor_id, "catalog.brand_create", brand.id, request_id)
            uow.commit()
            return brand

    def update_brand(self, identifier, data, actor_id, request_id=None):
        with self.uow_factory() as uow:
            brand = uow.catalog.brand(identifier)
            ensure_version(brand, data["version"])
            if "category_id" in data:
                uow.catalog.definition("categories", data["category_id"])
            for key, value in data.items():
                if key != "version":
                    setattr(brand, key, value)
            uow.catalog.save_brand(brand)
            uow.audit(actor_id, "catalog.brand_update", identifier, request_id)
            uow.commit()
            return brand

    @classmethod
    def _split_options(cls, data):
        options = {key: data.pop(key) for key in cls.OPTIONS if key in data}
        return data, options

    def create_product(self, data, actor_id, request_id=None):
        data, options = self._split_options(dict(data))
        with self.uow_factory() as uow:
            classifications = self._classification(uow.catalog, data["brand_id"])
            product = Product(id=uuid4(), classifications=classifications, **data)
            ensure_publishable(product)
            uow.catalog.add_product(product)
            for resource, slugs in options.items():
                uow.catalog.set_options(product.id, resource, slugs)
            uow.stock.ensure_decants(product.id)
            uow.audit(actor_id, "catalog.product_create", product.id, request_id)
            uow.commit()
            return uow.catalog.product(product.id)

    def product(self, identifier):
        with self.uow_factory() as uow:
            return uow.catalog.product(identifier)

    def update_product(self, identifier, data, actor_id, request_id=None):
        data, options = self._split_options(dict(data))
        with self.uow_factory() as uow:
            product = uow.catalog.product(identifier, lock=True)
            ensure_version(product, data["version"])
            if "brand_id" in data:
                uow.catalog.brand(data["brand_id"])
            for key, value in data.items():
                if key != "version":
                    setattr(product, key, value)
            product.classifications = self._classification(uow.catalog, product.brand_id)
            ensure_publishable(product)
            uow.catalog.save_product(product)
            for resource, slugs in options.items():
                uow.catalog.set_options(identifier, resource, slugs)
            uow.audit(actor_id, "catalog.product_update", identifier, request_id)
            uow.commit()
            return uow.catalog.product(identifier)

    def create_variant(self, product_id, data, actor_id, request_id=None):
        with self.uow_factory() as uow:
            uow.catalog.product(product_id, lock=True)
            if data["kind"] not in {"decant", "full_bottle"}:
                raise DomainError("INVALID_VARIANT", "Tipo de presentación inválido.")
            variant = Variant(id=uuid4(), product_id=product_id, **data)
            variant.volume_ml = decimal_value(variant.volume_ml, positive=True)
            variant.price = decimal_value(variant.price, positive=True)
            uow.catalog.add_variant(variant)
            if variant.kind == "full_bottle":
                uow.stock.ensure_bottles(variant.id)
            uow.audit(actor_id, "catalog.variant_create", variant.id, request_id)
            uow.commit()
            return variant

    def update_variant(self, identifier, data, actor_id, request_id=None):
        with self.uow_factory() as uow:
            variant = uow.catalog.variant(identifier)
            product = uow.catalog.product(variant.product_id, lock=True)
            ensure_version(variant, data["version"])
            for key, value in data.items():
                if key != "version":
                    setattr(variant, key, value)
            variant.price = decimal_value(variant.price, positive=True)
            product.variants = [variant if v.id == variant.id else v for v in product.variants]
            ensure_publishable(product)
            uow.catalog.save_variant(variant)
            uow.audit(actor_id, "catalog.variant_update", identifier, request_id)
            uow.commit()
            return variant

    def add_image(self, product_id, stream, data, actor_id, request_id=None):
        filename = None
        try:
            with self.uow_factory() as uow:
                product = uow.catalog.product(product_id, lock=True)
                if len(product.images) >= 5:
                    raise DomainError("IMAGE_LIMIT", "Se permiten cinco fotografías por perfume.")
                filename = self.storage.save(stream)
                asset, created = uow.media.register(
                    {
                        **self.storage.describe(filename),
                        "name": data.get("alt_es", ""),
                        "kind": "product",
                        "uploaded_by": actor_id,
                    }
                )
                image = ProductImage(
                    id=uuid4(),
                    product_id=product_id,
                    filename=asset.filename,
                    asset_id=asset.id,
                    url=asset.url,
                    **data,
                )
                uow.catalog.add_image(image)
                uow.audit(actor_id, "catalog.image_create", image.id, request_id)
                uow.commit()
                if not created:
                    self.storage.delete(filename)
                return image
        except Exception:
            if filename:
                self.storage.delete(filename)
            raise

    def attach_image(self, product_id, asset_id, data, actor_id, request_id=None):
        with self.uow_factory() as uow:
            product = uow.catalog.product(product_id, lock=True)
            if len(product.images) >= 5:
                raise DomainError("IMAGE_LIMIT", "Se permiten cinco fotografías por perfume.")
            asset = uow.media.asset(asset_id)
            if asset.kind != "product":
                raise DomainError("INVALID_ASSET", "Selecciona una fotografía de la biblioteca.")
            image = ProductImage(
                id=uuid4(),
                product_id=product_id,
                filename=asset.filename,
                asset_id=asset.id,
                url=asset.url,
                **data,
            )
            uow.catalog.add_image(image)
            uow.audit(actor_id, "catalog.image_attach", image.id, request_id)
            uow.commit()
            return image

    def update_image(self, identifier, data, actor_id, request_id=None):
        with self.uow_factory() as uow:
            image = uow.catalog.image(identifier)
            ensure_version(image, data["version"])
            for key, value in data.items():
                if key != "version":
                    setattr(image, key, value)
            uow.catalog.save_image(image)
            uow.audit(actor_id, "catalog.image_update", identifier, request_id)
            uow.commit()
            return image

    def delete_image(self, identifier, version, actor_id, request_id=None):
        with self.uow_factory() as uow:
            image = uow.catalog.image(identifier)
            ensure_version(image, version)
            uow.catalog.delete_image(identifier, version)
            uow.audit(actor_id, "catalog.image_delete", identifier, request_id)
            uow.commit()

    def visible_image(self, filename, *, private=False):
        with self.uow_factory() as uow:
            image = uow.catalog.image_by_filename(filename)
            product = uow.catalog.product(image.product_id)
            if not private and not product.visible:
                raise NotFound()
            return image
