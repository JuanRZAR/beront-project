from typing import Annotated

from pydantic import Field, StrictInt

from beront.shared.presentation.schemas import Identifier, Locale, Schema


class QuoteItem(Schema):
    variant_id: Identifier
    quantity: Annotated[StrictInt, Field(ge=1, le=20)]


class QuoteBody(Schema):
    locale: Locale = "es"
    items: Annotated[list[QuoteItem], Field(min_length=1, max_length=400)]
