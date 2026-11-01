from beront.modules.cart.domain.entities import CartQuote, QuoteLine
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
            QuoteLine(v.id, p.brand_name, p.name, v.kind, v.volume_ml, quantity, v.price)
            for p, v, quantity in selected
        ]
        url = self.whatsapp.build(lines, locale)
        return CartQuote(lines, url, None if url else "WHATSAPP_NOT_CONFIGURED")
