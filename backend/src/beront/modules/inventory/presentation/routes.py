from flask import Blueprint, current_app, g

from beront.modules.identity.presentation.decorators import require_auth, require_permission
from beront.modules.inventory.presentation.schemas import AdjustmentBody
from beront.modules.inventory.presentation.serializers import balance_data, movement_data
from beront.shared.presentation.schemas import PageQuery, json_body, query_body


def make_blueprint():
    bp = Blueprint("inventory", __name__, url_prefix="/api/v1/admin/inventory")

    @bp.get("")
    @require_auth
    @require_permission("inventory:read")
    def balances():
        params = query_body(PageQuery)
        items, total = current_app.extensions["beront"].inventory.list_balances(**params)
        return {"data": [balance_data(item) for item in items], "meta": {**params, "total": total}}

    @bp.get("/movements")
    @require_auth
    @require_permission("inventory:read")
    def movements():
        params = query_body(PageQuery)
        items, total = current_app.extensions["beront"].inventory.list_movements(**params)
        return {"data": [movement_data(item) for item in items], "meta": {**params, "total": total}}

    @bp.post("/adjustments")
    @require_auth
    @require_permission("inventory:adjust")
    def adjust():
        data = json_body(AdjustmentBody)
        movement, created = current_app.extensions["beront"].inventory.adjust(
            **data,
            actor_id=g.admin.id,
            request_id=g.request_id,
        )
        return {"data": movement_data(movement)}, 201 if created else 200

    return bp
