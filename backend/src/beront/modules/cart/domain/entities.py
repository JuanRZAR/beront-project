from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class QuoteOption:
    variant_id: UUID
    volume_ml: Decimal
    unit_price: Decimal


@dataclass(frozen=True)
class QuoteLine:
    variant_id: UUID
    brand_name: str
    product_name: str
    kind: str
    volume_ml: Decimal
    quantity: int
    unit_price: Decimal
    product_slug: str = ""
    image_url: str | None = None
    options: tuple[QuoteOption, ...] = ()

    @property
    def line_total(self):
        return self.unit_price * self.quantity


@dataclass(frozen=True)
class CartQuote:
    items: list[QuoteLine]
    whatsapp_url: str | None
    configuration_error: str | None = None
    currency: str = "USD"

    @property
    def total(self):
        return sum((item.line_total for item in self.items), Decimal("0.00"))
