import json

from flask import Blueprint, current_app, g, request
from werkzeug.exceptions import UnsupportedMediaType

from beront.modules.identity.presentation.decorators import require_auth, require_permission
from beront.modules.orders.presentation.schemas import (
    CheckoutQuote,
    FlowCreate,
    FlowPatch,
    OrderCreate,
    OrderQuery,
    OrderTransition,
    PaymentApproval,
    RecoveryBody,
    ShippingPatch,
    StatusCreate,
    StatusPatch,
    TrackBody,
)
from beront.modules.orders.presentation.serializers import private_order, public_order
from beront.shared.domain.errors import DomainError, NotFound
from beront.shared.presentation.schemas import json_body, query_body
from beront.shared.presentation.security import client_address


def services():
    return current_app.extensions["beront"]


def photo():
    if request.mimetype != "multipart/form-data":
        raise UnsupportedMediaType()
    if set(request.files) != {"file"} or len(request.files.getlist("file")) != 1:
        raise DomainError("RECEIPT_REQUIRED", "Adjunta una sola fotografía en el campo file.")
    return request.files["file"].stream


def make_blueprint(csrf, limiter):
    bp = Blueprint("orders", __name__)

    @bp.post("/api/v1/checkout/quote")
    @csrf.exempt
    @limiter.limit("30 per minute")
    def quote():
        return {"data": services().orders.quote(json_body(CheckoutQuote))}

    @bp.post("/api/v1/orders")
    @limiter.limit("10 per minute")
    def create():
        stream = None
        if request.is_json:
            data = json_body(OrderCreate)
        else:
            stream = photo()
            if set(request.form) != {"payload"} or len(request.form.getlist("payload")) != 1:
                raise DomainError(
                    "VALIDATION_ERROR", "Envía el formulario en payload y la fotografía en file."
                )
            try:
                payload = json.loads(request.form["payload"])
            except (ValueError, TypeError) as error:
                raise DomainError(
                    "VALIDATION_ERROR", "El formulario no contiene JSON válido."
                ) from error
            data = OrderCreate.model_validate(payload).model_dump()
        order, created = services().orders.create(data, stream)
        return {
            "data": public_order(order, services().commerce.whatsapp_number())
        }, 201 if created else 200

    @bp.post("/api/v1/orders/track")
    @csrf.exempt
    @limiter.limit("20 per minute")
    def track():
        data = json_body(TrackBody)
        return {
            "data": public_order(
                services().orders.track(data["code"]), services().commerce.whatsapp_number()
            )
        }

    @bp.post("/api/v1/orders/recovery")
    @limiter.limit("5 per hour")
    def recover():
        services().orders.recover(json_body(RecoveryBody)["cedula"], client_address())
        return {
            "data": {
                "message": "Si hay pedidos asociados, enviaremos el código al correo registrado."
            }
        }, 202

    @bp.get("/api/v1/admin/orders")
    @require_auth
    @require_permission("orders:read")
    def listing():
        query = query_body(OrderQuery)
        result = services().orders.listing(query)
        return {
            "data": [private_order(row) for row in result["items"]],
            "meta": {
                "total": result["total"],
                "page": query["page"],
                "page_size": query["page_size"],
            },
        }

    @bp.get("/api/v1/admin/orders/<uuid:identifier>")
    @require_auth
    @require_permission("orders:read")
    def detail(identifier):
        return {"data": private_order(services().orders.get(identifier))}

    @bp.post("/api/v1/admin/orders/<uuid:identifier>/approve-payment")
    @require_auth
    @require_permission("orders:approve_payment")
    def approve(identifier):
        order, result = services().orders.approve_payment(
            identifier, json_body(PaymentApproval), g.admin.id, g.request_id
        )
        return {"data": private_order(order), "payment_result": result}

    @bp.post("/api/v1/admin/orders/<uuid:identifier>/transition")
    @require_auth
    @require_permission("orders:manage")
    def transition(identifier):
        data = OrderTransition.model_validate(request.get_json()).model_dump(exclude_none=True)
        return {
            "data": private_order(
                services().orders.transition(identifier, data, g.admin.id, g.request_id)
            )
        }

    @bp.patch("/api/v1/admin/orders/<uuid:identifier>/shipping")
    @require_auth
    @require_permission("orders:manage")
    def shipping(identifier):
        return {
            "data": private_order(
                services().orders.update_shipping(
                    identifier, json_body(ShippingPatch), g.admin.id, g.request_id
                )
            )
        }

    @bp.post("/api/v1/admin/orders/<uuid:identifier>/receipts")
    @require_auth
    @require_permission("orders:manage")
    def receipt(identifier):
        stream = photo()
        if request.form:
            raise DomainError("VALIDATION_ERROR", "El comprobante solo utiliza el campo file.")
        return {
            "data": private_order(
                services().orders.add_receipt(identifier, stream, g.admin.id, g.request_id)
            )
        }, 201

    @bp.get("/api/v1/admin/order-flow/<resource>")
    @require_auth
    @require_permission("commerce:write")
    def definitions(resource):
        return {"data": services().orders.definitions(resource)}

    @bp.post("/api/v1/admin/order-flow/<resource>")
    @require_auth
    @require_permission("commerce:write")
    def create_definition(resource):
        if resource not in {"statuses", "transitions"}:
            raise NotFound()
        schema = StatusCreate if resource == "statuses" else FlowCreate
        return {
            "data": services().orders.create_definition(
                resource, json_body(schema), g.admin.id, g.request_id
            )
        }, 201

    @bp.patch("/api/v1/admin/order-flow/<resource>/<uuid:identifier>")
    @require_auth
    @require_permission("commerce:write")
    def update_definition(resource, identifier):
        if resource not in {"statuses", "transitions"}:
            raise NotFound()
        schema = StatusPatch if resource == "statuses" else FlowPatch
        return {
            "data": services().orders.update_definition(
                resource, identifier, json_body(schema), g.admin.id, g.request_id
            )
        }

    return bp
