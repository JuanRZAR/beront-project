from typing import Annotated

from pydantic import Field, StrictBool, model_validator

from beront.shared.presentation.schemas import (
    Audience,
    CatalogKey,
    Classification,
    DecimalInput,
    Identifier,
    Kind,
    Locale,
    Name,
    PageQuery,
    PatchSchema,
    PositiveDecimal,
    Schema,
)


class BrandCreate(Schema):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    category_id: Identifier
    active: StrictBool = True


class BrandPatch(PatchSchema):
    name: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    active: StrictBool | None = None
    category_id: Identifier | None = None


class DefinitionCreate(Schema):
    slug: CatalogKey
    name_es: Annotated[str, Field(min_length=1, max_length=100)]
    name_en: Annotated[str, Field(min_length=1, max_length=100)]
    active: StrictBool = True


class DefinitionPatch(PatchSchema):
    name_es: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    name_en: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    active: StrictBool | None = None


class PresentationCreate(Schema):
    name_es: Annotated[str, Field(min_length=1, max_length=100)]
    name_en: Annotated[str, Field(min_length=1, max_length=100)]
    kind: Kind
    volume_ml: PositiveDecimal
    active: StrictBool = True


OptionSlugs = Annotated[list[CatalogKey], Field(max_length=20)]


def unique_slugs(model):
    for key in ("accords", "usages", "profiles"):
        values = getattr(model, key)
        if values is not None and len(set(values)) != len(values):
            raise ValueError("No repitas opciones de clasificación.")
    return model


class ProductCreate(Schema):
    brand_id: Identifier
    name: Name
    slug: Annotated[str, Field(min_length=1, max_length=160, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
    audience: Audience
    accords: OptionSlugs = []
    usages: OptionSlugs = []
    profiles: OptionSlugs = []
    description_es: Annotated[str, Field(max_length=5000)] = ""
    description_en: Annotated[str, Field(max_length=5000)] = ""

    @model_validator(mode="after")
    def distinct_options(self):
        return unique_slugs(self)


class ProductPatch(PatchSchema):
    brand_id: Identifier | None = None
    name: Name | None = None
    slug: (
        Annotated[str, Field(min_length=1, max_length=160, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
        | None
    ) = None
    audience: Audience | None = None
    accords: OptionSlugs | None = None
    usages: OptionSlugs | None = None
    profiles: OptionSlugs | None = None
    description_es: Annotated[str, Field(max_length=5000)] | None = None
    description_en: Annotated[str, Field(max_length=5000)] | None = None
    published: StrictBool | None = None
    archived: StrictBool | None = None
    sold_out: StrictBool | None = None

    @model_validator(mode="after")
    def distinct_options(self):
        return unique_slugs(self)


class VariantCreate(Schema):
    kind: Kind
    volume_ml: PositiveDecimal
    price: PositiveDecimal
    active: StrictBool = True
    sold_out: StrictBool = False


class VariantPatch(PatchSchema):
    price: PositiveDecimal | None = None
    active: StrictBool | None = None
    sold_out: StrictBool | None = None


class ImageCreate(Schema):
    position: Annotated[int, Field(ge=0, le=100)] = 0
    alt_es: Annotated[str, Field(max_length=250)] = ""
    alt_en: Annotated[str, Field(max_length=250)] = ""


class ImageAttach(ImageCreate):
    asset_id: Identifier


class ImagePatch(PatchSchema):
    position: Annotated[int, Field(ge=0, le=100)] | None = None
    alt_es: Annotated[str, Field(max_length=250)] | None = None
    alt_en: Annotated[str, Field(max_length=250)] | None = None


class CatalogQuery(PageQuery):
    q: Annotated[str, Field(max_length=120)] = ""
    kind: list[Kind] = []
    brand_id: list[Identifier] = []
    classification: list[Classification] = []
    audience: list[Audience] = []
    accord: list[CatalogKey] = []
    usage: list[CatalogKey] = []
    profile: list[CatalogKey] = []
    volume_ml: list[PositiveDecimal] = []
    min_price: DecimalInput | None = None
    max_price: DecimalInput | None = None
    available: bool | None = None
    sort: str = "name"
    locale: Locale = "es"

    @model_validator(mode="after")
    def bounds(self):
        if self.sort not in {"name", "price_asc", "price_desc"}:
            raise ValueError("Orden no admitido.")
        if any(value is not None and value < 0 for value in (self.min_price, self.max_price)):
            raise ValueError("El precio no puede ser negativo.")
        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise ValueError("El precio mínimo excede el máximo.")
        if any(
            len(getattr(self, key)) > 50
            for key in (
                "kind",
                "brand_id",
                "classification",
                "audience",
                "accord",
                "usage",
                "profile",
                "volume_ml",
            )
        ):
            raise ValueError("Demasiados valores de filtro.")
        return self


class LocaleQuery(Schema):
    locale: Locale = "es"
