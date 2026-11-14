from flask import Blueprint, current_app, g

from beront.modules.commerce.presentation.messages import MessageCreate, MessageSave
from beront.modules.commerce.presentation.schemas import (
    BankCreate,
    BankPatch,
    CityCreate,
    CityPatch,
    ProvinceCreate,
    ProvincePatch,
    SettingsBody,
)
from beront.modules.identity.presentation.decorators import require_auth, require_permission
from beront.shared.domain.errors import NotFound
from beront.shared.presentation.schemas import json_body

SCHEMAS = {
    "provinces": (ProvinceCreate, ProvincePatch),
    "cities": (CityCreate, CityPatch),
    "banks": (BankCreate, BankPatch),
}


def service():
    return current_app.extensions["beront"].commerce


def make_blueprint():
    bp = Blueprint("commerce", __name__)

    @bp.get("/api/v1/home/messages")
    def home_messages():
        return {"data": current_app.extensions["beront"].featured.listing()}

    @bp.get("/api/v1/admin/home/messages")
    @require_auth
    @require_permission("commerce:write")
    def admin_messages():
        return {"data": current_app.extensions["beront"].featured.listing(private=True)}

    @bp.post("/api/v1/admin/home/messages")
    @require_auth
    @require_permission("commerce:write")
    def add_message():
        return {
            "data": current_app.extensions["beront"].featured.create(
                json_body(MessageCreate), g.admin.id, g.request_id
            )
        }, 201

    @bp.put("/api/v1/admin/home/messages/<uuid:identifier>")
    @require_auth
    @require_permission("commerce:write")
    def save_message(identifier):
        return {
            "data": current_app.extensions["beront"].featured.save(
                identifier, json_body(MessageSave), g.admin.id, g.request_id
            )
        }

    @bp.get("/api/v1/checkout/options")
    def options():
        return {"data": service().options()}

    @bp.get("/api/v1/admin/settings")
    @require_auth
    @require_permission("commerce:write")
    def settings():
        return {"data": service().settings()}

    @bp.put("/api/v1/admin/settings")
    @require_auth
    @require_permission("commerce:write")
    def save_settings():
        return {"data": service().save_settings(json_body(SettingsBody), g.admin.id, g.request_id)}

    @bp.get("/api/v1/admin/commerce/<resource>")
    @require_auth
    @require_permission("commerce:write")
    def listing(resource):
        return {"data": service().listing(resource, private=True)}

    @bp.post("/api/v1/admin/commerce/<resource>")
    @require_auth
    @require_permission("commerce:write")
    def create(resource):
        if resource not in SCHEMAS:
            raise NotFound()
        return {
            "data": service().create(
                resource, json_body(SCHEMAS[resource][0]), g.admin.id, g.request_id
            )
        }, 201

    @bp.patch("/api/v1/admin/commerce/<resource>/<uuid:identifier>")
    @require_auth
    @require_permission("commerce:write")
    def update(resource, identifier):
        if resource not in SCHEMAS:
            raise NotFound()
        return {
            "data": service().update(
                resource, identifier, json_body(SCHEMAS[resource][1]), g.admin.id, g.request_id
            )
        }

    return bp
