from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from flask import request
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StrictInt, model_validator

from beront.shared.domain.values import decimal_value


def parse_decimal(value):
    if not isinstance(value, (str, Decimal)):
        raise ValueError("Envía el decimal como cadena.")
    return decimal_value(value)


DecimalInput = Annotated[Decimal, BeforeValidator(parse_decimal)]
PositiveDecimal = Annotated[DecimalInput, Field(gt=0)]
Version = Annotated[StrictInt, Field(ge=1)]
Locale = Literal["es", "en"]
Kind = Literal["decant", "full_bottle"]
CatalogKey = Annotated[
    str, Field(min_length=1, max_length=64, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
]
Audience = CatalogKey
Classification = CatalogKey
Name = Annotated[str, Field(min_length=1, max_length=120, pattern=r"^[^\x00-\x1f\x7f]+$")]


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PatchSchema(Schema):
    version: Version

    @model_validator(mode="after")
    def provided_values(self):
        if len(self.model_fields_set) < 2:
            raise ValueError("Incluye al menos un campo para editar.")
        if any(getattr(self, key) is None for key in self.model_fields_set):
            raise ValueError("Los campos editados no admiten null.")
        return self


class PageQuery(Schema):
    page: Annotated[int, Field(ge=1, le=10000)] = 1
    page_size: Annotated[int, Field(ge=1, le=48)] = 24


class VersionBody(Schema):
    version: Version


def json_body(schema):
    return schema.model_validate(request.get_json()).model_dump(
        exclude_unset=issubclass(schema, PatchSchema)
    )


def query_body(schema, repeatable=()):
    data = {}
    for key in request.args:
        values = request.args.getlist(key)
        if key not in repeatable and len(values) != 1:
            from beront.shared.domain.errors import DomainError

            raise DomainError("VALIDATION_ERROR", "El parámetro no admite valores repetidos.")
        data[key] = values if key in repeatable else values[0]
    return schema.model_validate(data).model_dump()


Identifier = UUID
