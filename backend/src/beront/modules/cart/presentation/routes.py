from flask import Blueprint, current_app

from beront.modules.cart.presentation.schemas import QuoteBody
from beront.modules.cart.presentation.serializers import quote_data


def make_blueprint(csrf, limiter):
    bp = Blueprint("cart", __name__, url_prefix="/api/v1/cart")

    @bp.post("/quote")
    @csrf.exempt
    @limiter.limit("30 per minute")
    def quote():
        from flask import request

        data = QuoteBody.model_validate(request.get_json())
        result = current_app.extensions["beront"].quote.execute(
            [item.model_dump() for item in data.items],
            data.locale,
        )
        return {"data": quote_data(result)}

    return bp
