from dataclasses import dataclass
from decimal import Decimal

from beront.modules.catalog.domain.entities import Product, Variant
from beront.modules.inventory.application.availability import StockAvailability
from beront.modules.inventory.application.contracts import StockRequirement
from beront.shared.domain.errors import NotFound


@dataclass
class ProductView:
    product: Product
    variants: list[Variant]
    availability: dict

    @property
    def minimum_price(self):
        return min((variant.price for variant in self.variants), default=Decimal("0"))


def matching_variants(product, filters, *, private=False):
    return [
        variant
        for variant in product.variants
        if (private or (variant.active and variant.presentation_active))
        and (not filters.get("kind") or variant.kind in filters["kind"])
        and (not filters.get("volume_ml") or variant.volume_ml in filters["volume_ml"])
        and (filters.get("min_price") is None or variant.price >= filters["min_price"])
        and (filters.get("max_price") is None or variant.price <= filters["max_price"])
    ]


class CatalogQueryFacade:
    def __init__(self, uow_factory):
        self.uow_factory = uow_factory

    @staticmethod
    def _availability(products, repository):
        requirements = [
            StockRequirement(p.id, v.id, v.kind, v.volume_ml) for p in products for v in p.variants
        ]
        availability = StockAvailability(repository).inspect(requirements)
        for product in products:
            for variant in product.variants:
                availability[variant.id] = (
                    product.visible
                    and not product.sold_out
                    and variant.active
                    and variant.presentation_active
                    and not variant.sold_out
                    and availability.get(variant.id, False)
                )
        return availability

    def search(self, filters, *, private=False):
        views = []
        with self.uow_factory() as uow:
            offset = 0
            while True:
                products = uow.catalog.candidates(
                    filters, private=private, offset=offset, limit=100
                )
                if not products:
                    break
                availability = self._availability(products, uow.stock)
                for product in products:
                    variants = matching_variants(product, filters, private=private)
                    if filters.get("available") is not None:
                        variants = [
                            v for v in variants if availability[v.id] == filters["available"]
                        ]
                    if variants or (private and filters.get("available") is None):
                        views.append(
                            ProductView(
                                product, variants, {v.id: availability[v.id] for v in variants}
                            )
                        )
                offset += len(products)
            order = filters.get("sort", "name")
            if order in {"price_asc", "price_desc"}:
                sign = -1 if order == "price_desc" else 1
                views.sort(
                    key=lambda view: (
                        sign * view.minimum_price,
                        view.product.name.casefold(),
                        view.product.id,
                    )
                )
            page, size = filters.get("page", 1), filters.get("page_size", 24)
            return views[(page - 1) * size : page * size], len(views)

    def detail(self, slug):
        with self.uow_factory() as uow:
            product = uow.catalog.by_slug(slug)
            if not product.visible:
                raise NotFound()
            variants = [v for v in product.variants if v.active and v.presentation_active]
            return ProductView(product, variants, self._availability([product], uow.stock))

    def facets(self):
        with self.uow_factory() as uow:
            sizes, houses = set(), {}
            offset = 0
            while products := uow.catalog.candidates({}, offset=offset, limit=100):
                for product in products:
                    houses[product.brand_id] = product.brand_name
                    sizes.update(v.volume_ml for v in product.variants if v.active)
                offset += len(products)
            return {
                "brands": [
                    {"id": str(key), "name": value}
                    for key, value in sorted(houses.items(), key=lambda item: item[1].casefold())
                ],
                "volumes_ml": [format(size, ".2f") for size in sorted(sizes)],
                "classifications": [row["slug"] for row in uow.catalog.definitions("categories")],
                "audiences": [row["slug"] for row in uow.catalog.definitions("audiences")],
                "accords": [row["slug"] for row in uow.catalog.definitions("accords")],
                "usages": [row["slug"] for row in uow.catalog.definitions("usages")],
                "profiles": [row["slug"] for row in uow.catalog.definitions("profiles")],
                "kinds": sorted({row["kind"] for row in uow.catalog.definitions("presentations")}),
                "definitions": {
                    key: uow.catalog.definitions(key)
                    for key in (
                        "categories",
                        "audiences",
                        "presentations",
                        "accords",
                        "usages",
                        "profiles",
                    )
                },
            }

    def quote_selection(self, quantities):
        with self.uow_factory() as uow:
            return self.selection_in(uow, quantities)

    @staticmethod
    def selection_in(uow, quantities):
        products = {}
        selected = []
        problems = []
        for variant_id, quantity in quantities.items():
            try:
                variant = uow.catalog.variant(variant_id)
                if variant.product_id not in products:
                    products[variant.product_id] = uow.catalog.product(variant.product_id)
                product = products[variant.product_id]
                if (
                    not product.visible
                    or product.sold_out
                    or not variant.active
                    or not variant.presentation_active
                    or variant.sold_out
                ):
                    raise NotFound()
                selected.append((product, variant, quantity))
            except NotFound:
                problems.append(
                    {
                        "field": "items",
                        "variant_id": str(variant_id),
                        "code": "UNAVAILABLE_PRODUCT",
                    }
                )
        requirements = [
            StockRequirement(p.id, v.id, v.kind, v.volume_ml, quantity)
            for p, v, quantity in selected
        ]
        available = StockAvailability(uow.stock).inspect(requirements, aggregate=True)
        for _, variant, _ in selected:
            if not available.get(variant.id, False):
                problems.append(
                    {
                        "field": "items",
                        "variant_id": str(variant.id),
                        "code": "UNAVAILABLE_QUANTITY",
                    }
                )
        return selected, problems
