from decimal import Decimal
from uuid import UUID

from beront.modules.catalog.domain.entities import Brand, Product, ProductImage, Variant
from beront.shared.infrastructure.pg_call import require_record

OPTION_FIELDS = ("accords", "usages", "profiles")


def to_brand(row):
    return Brand(
        UUID(row["id"]), row["name"], row["active"], row["version"], UUID(row["category_id"])
    )


def to_variant(row):
    values = {key: row[key] for key in Variant.__dataclass_fields__}
    for key in ("id", "product_id"):
        values[key] = UUID(values[key])
    for key in ("volume_ml", "price"):
        values[key] = Decimal(values[key])
    return Variant(**values)


def to_image(row):
    values = {key: row[key] for key in ProductImage.__dataclass_fields__}
    for key in ("id", "product_id", "asset_id"):
        values[key] = UUID(values[key])
    return ProductImage(**values)


def to_product(row):
    values = {
        key: row[key] for key in Product.__dataclass_fields__ if key not in {"variants", "images"}
    }
    values["id"], values["brand_id"] = UUID(values["id"]), UUID(values["brand_id"])
    values["variants"] = [to_variant(v) for v in row["variants"]]
    values["images"] = [to_image(i) for i in row["images"]]
    return Product(**values)


def product_values(product):
    return {
        key: value
        for key, value in vars(product).items()
        if key not in {"variants", "images", "brand_name", "brand_active", *OPTION_FIELDS}
    }


class SqlCatalogRepository:
    DEFINITIONS = {
        "categories": "category",
        "audiences": "audience",
        "presentations": "presentation",
    }
    OPTION_DIMENSIONS = {"accords": "accord", "usages": "usage", "profiles": "profile"}

    def __init__(self, pg):
        self.pg = pg

    def _definition_call(self, resource, action, values):
        if resource in self.OPTION_DIMENSIONS:
            return self.pg.call(
                "catalog_option_" + action,
                {**values, "dimension": self.OPTION_DIMENSIONS[resource]},
            )
        return self.pg.call("catalog_" + self.DEFINITIONS[resource] + "_" + action, values)

    def definitions(self, resource, *, private=False):
        return self._definition_call(resource, "list", {"private": private})

    def definition(self, resource, identifier):
        return require_record(self._definition_call(resource, "get", {"id": identifier}))

    def add_definition(self, resource, values):
        return self._definition_call(resource, "add", values)

    def save_definition(self, resource, values):
        return self._definition_call(resource, "save", values)

    def set_options(self, product_id, resource, slugs):
        self.pg.call(
            "catalog_product_options_set",
            {
                "product_id": product_id,
                "dimension": self.OPTION_DIMENSIONS[resource],
                "slugs": slugs,
            },
        )

    def product(self, product_id, *, lock=False):
        return to_product(
            require_record(self.pg.call("catalog_product_get", {"id": product_id, "lock": lock}))
        )

    def by_slug(self, slug):
        return to_product(require_record(self.pg.call("catalog_product_by_slug", {"slug": slug})))

    def candidates(self, filters, *, private=False, offset=0, limit=100):
        rows = self.pg.call(
            "catalog_candidates",
            {"filters": filters, "private": private, "offset": offset, "limit": limit},
        )
        return [to_product(row) for row in rows]

    def add_product(self, product):
        self.pg.call("catalog_product_add", product_values(product))

    def save_product(self, product):
        product.version = self.pg.call("catalog_product_save", product_values(product))["version"]

    def variant(self, variant_id):
        return to_variant(require_record(self.pg.call("catalog_variant_get", {"id": variant_id})))

    def add_variant(self, variant):
        self.pg.call("catalog_variant_add", vars(variant))

    def save_variant(self, variant):
        variant.version = self.pg.call("catalog_variant_save", vars(variant))["version"]

    def brands(self, *, private=False):
        return [to_brand(row) for row in self.pg.call("catalog_brands", {"private": private})]

    def brand(self, brand_id):
        return to_brand(require_record(self.pg.call("catalog_brand_get", {"id": brand_id})))

    def add_brand(self, brand):
        self.pg.call("catalog_brand_add", {**vars(brand), "normalized_name": brand.name.casefold()})

    def save_brand(self, brand):
        brand.version = self.pg.call(
            "catalog_brand_save", {**vars(brand), "normalized_name": brand.name.casefold()}
        )["version"]

    def add_image(self, image):
        self.pg.call("catalog_image_add", vars(image))

    def image(self, image_id):
        return to_image(require_record(self.pg.call("catalog_image_get", {"id": image_id})))

    def image_by_filename(self, filename):
        return to_image(
            require_record(self.pg.call("catalog_image_by_filename", {"filename": filename}))
        )

    def save_image(self, image):
        image.version = self.pg.call("catalog_image_save", vars(image))["version"]

    def delete_image(self, image_id, version):
        self.pg.call("catalog_image_delete", {"id": image_id, "version": version})
