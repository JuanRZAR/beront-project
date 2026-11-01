from typing import Annotated, Literal

from pydantic import Field, StrictBool, model_validator

from beront.modules.cart.presentation.schemas import QuoteBody
from beront.shared.presentation.schemas import (
    CatalogKey,
    Identifier,
    Name,
    PageQuery,
    PatchSchema,
    Schema,
    VersionBody,
)

Cedula = Annotated[str, Field(pattern=r"^[0-9]{10}$")]


class CustomerBody(Schema):
    cedula: Cedula
    first_name: Annotated[Name, Field(max_length=100)]
    last_name: Annotated[Name, Field(max_length=100)]
    phone: Annotated[str, Field(pattern=r"^\+?[0-9]{7,15}$")]
    email: Annotated[str, Field(max_length=254, pattern=r"^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$")]


class CheckoutQuote(QuoteBody):
    city_id: Identifier


class OrderCreate(CheckoutQuote):
    operation_id: Identifier
    quote_token: Annotated[str, Field(max_length=57344, pattern=r"^[A-Za-z0-9_-]+\.[a-f0-9]{64}$")]
    customer: CustomerBody
    address: Annotated[str, Field(max_length=300, pattern=r"^[^\x00-\x1f\x7f]*$")] = ""
    payment_method: Literal["bank_transfer", "whatsapp"]
    bank_id: Identifier | None = None
    terms_accepted: StrictBool

    @model_validator(mode="after")
    def payment_details(self):
        if not self.terms_accepted:
            raise ValueError("Acepta los términos de prueba para continuar.")
        if self.payment_method == "bank_transfer" and self.bank_id is None:
            raise ValueError("Selecciona la cuenta bancaria.")
        if self.payment_method == "whatsapp" and self.bank_id is not None:
            raise ValueError(
                "El pago por WhatsApp no utiliza una cuenta bancaria en este formulario."
            )
        return self


class TrackBody(Schema):
    code: Annotated[str, Field(pattern=r"^BRT-[A-Za-z0-9_-]{24}$")]


class RecoveryBody(Schema):
    cedula: Cedula


class OrderQuery(PageQuery):
    q: Annotated[str, Field(max_length=100)] = ""
    status_id: Identifier | None = None


class PaymentApproval(VersionBody):
    status_id: Identifier


class OrderTransition(PaymentApproval):
    guide_number: Annotated[str, Field(max_length=100)] | None = None
    tracking_number: Annotated[str, Field(max_length=100)] | None = None


class ShippingPatch(VersionBody):
    guide_number: Annotated[str, Field(min_length=1, max_length=100)]
    tracking_number: Annotated[str, Field(min_length=1, max_length=100)]


class StatusCreate(Schema):
    slug: CatalogKey
    name_es: Annotated[str, Field(min_length=1, max_length=100)]
    name_en: Annotated[str, Field(min_length=1, max_length=100)]
    phase: Literal["awaiting_payment", "paid", "shipped", "delivered", "cancelled", "stock_issue"]
    purpose: Literal["bank_transfer", "whatsapp", "stock_issue"] | None = None
    active: StrictBool = True


class StatusPatch(PatchSchema):
    name_es: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    name_en: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    active: StrictBool | None = None


class FlowCreate(Schema):
    from_status_id: Identifier
    to_status_id: Identifier
    active: StrictBool = True


class FlowPatch(PatchSchema):
    active: StrictBool | None = None
