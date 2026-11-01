from typing import Annotated

from pydantic import Field, StrictBool, StrictInt

from beront.shared.presentation.schemas import DecimalInput, Identifier, PatchSchema, Schema

Text100 = Annotated[str, Field(min_length=1, max_length=100, pattern=r"^[^\x00-\x1f\x7f]+$")]


class SettingsBody(Schema):
    version: Annotated[StrictInt, Field(ge=0)]
    whatsapp_number: Annotated[str, Field(max_length=15)]
    terms_es: Annotated[str, Field(max_length=20000)]
    terms_en: Annotated[str, Field(max_length=20000)]


class ProvinceCreate(Schema):
    code: Annotated[str, Field(pattern=r"^[0-9]{2}$")]
    name: Text100
    mainland: StrictBool
    active: StrictBool = True


class ProvincePatch(PatchSchema):
    name: Text100 | None = None
    active: StrictBool | None = None


class CityCreate(Schema):
    province_id: Identifier
    name: Text100
    shipping_fee: Annotated[DecimalInput, Field(ge=0)]
    active: StrictBool = True


class CityPatch(PatchSchema):
    name: Text100 | None = None
    shipping_fee: Annotated[DecimalInput, Field(ge=0)] | None = None
    active: StrictBool | None = None


class BankCreate(Schema):
    bank_name: Text100
    account_type: Annotated[str, Field(min_length=1, max_length=80)]
    account_number: Annotated[str, Field(min_length=1, max_length=60)]
    holder_name: Annotated[str, Field(min_length=1, max_length=160)]
    holder_identification: Annotated[str, Field(min_length=1, max_length=30)]
    active: StrictBool = True


class BankPatch(PatchSchema):
    bank_name: Text100 | None = None
    account_type: Annotated[str, Field(min_length=1, max_length=80)] | None = None
    account_number: Annotated[str, Field(min_length=1, max_length=60)] | None = None
    holder_name: Annotated[str, Field(min_length=1, max_length=160)] | None = None
    holder_identification: Annotated[str, Field(min_length=1, max_length=30)] | None = None
    active: StrictBool | None = None
