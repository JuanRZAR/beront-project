from beront.modules.cart.domain.entities import CartQuote, QuoteLine, QuoteOption
from beront.modules.cart.domain.policies import consolidate_items
from beront.shared.domain.errors import DomainError


class BuildCartQuote:
    def __init__(self, catalog, whatsapp):
        self.catalog, self.whatsapp = catalog, whatsapp

    def execute(self, items, locale):
        quantities = consolidate_items(items)
        selected, problems = self.catalog.quote_selection(quantities)
        if problems:
            raise DomainError(
                "INSUFFICIENT_STOCK", "La disponibilidad del carrito ha cambiado.", problems
            )
        lines = [
            QuoteLine(
                v.id,
                p.brand_name,
                p.name,
                v.kind,
                v.volume_ml,
                quantity,
                v.price,
                p.slug,
                self.first_image(p),
                self.options(p, v.kind),
            )
            for p, v, quantity in selected
        ]
        url = self.whatsapp.build(lines, locale)
        return CartQuote(lines, url, None if url else "WHATSAPP_NOT_CONFIGURED")

    @staticmethod
    def first_image(product):
        images = sorted(product.images, key=lambda image: image.position)
        return images[0].url if images else None

    @staticmethod
    def options(product, kind):
        return tuple(
            QuoteOption(v.id, v.volume_ml, v.price)
            for v in sorted(product.variants, key=lambda v: v.volume_ml)
            if v.kind == kind and v.active and v.presentation_active and not v.sold_out
        )
