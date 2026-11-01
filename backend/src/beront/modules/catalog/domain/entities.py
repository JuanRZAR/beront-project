from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID


@dataclass
class Brand:
    id: UUID
    name: str
    active: bool = True
    version: int = 1
    category_id: UUID | None = None


@dataclass
class Variant:
    id: UUID
    product_id: UUID
    kind: str
    volume_ml: Decimal
    price: Decimal
    active: bool = True
    sold_out: bool = False
    version: int = 1
    presentation_active: bool = True


@dataclass
class ProductImage:
    id: UUID
    product_id: UUID
    filename: str
    position: int = 0
    alt_es: str = ""
    alt_en: str = ""
    version: int = 1
    asset_id: UUID | None = None
    url: str = ""


@dataclass
class Product:
    id: UUID
    brand_id: UUID
    name: str
    slug: str
    audience: str
    classifications: list[str]
    accords: list[str] = field(default_factory=list)
    usages: list[str] = field(default_factory=list)
    profiles: list[str] = field(default_factory=list)
    description_es: str = ""
    description_en: str = ""
    published: bool = False
    archived: bool = False
    sold_out: bool = False
    version: int = 1
    brand_name: str = ""
    brand_active: bool = True
    variants: list[Variant] = field(default_factory=list)
    images: list[ProductImage] = field(default_factory=list)

    @property
    def visible(self):
        return self.published and not self.archived and self.brand_active
