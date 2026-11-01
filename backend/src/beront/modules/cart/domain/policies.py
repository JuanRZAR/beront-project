from collections import defaultdict

from beront.shared.domain.errors import DomainError


def consolidate_items(items):
    quantities = defaultdict(int)
    for item in items:
        quantity = item["quantity"]
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise DomainError("INVALID_QUANTITY", "Usa cantidades enteras positivas.")
        quantities[item["variant_id"]] += quantity
    if (
        not quantities
        or len(quantities) > 20
        or any(quantity > 20 for quantity in quantities.values())
    ):
        raise DomainError(
            "CART_LIMIT", "Se permiten 20 presentaciones y hasta 20 unidades por presentación."
        )
    return dict(quantities)
