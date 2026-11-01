from urllib.parse import quote


def public_order(order, number=""):
    result = {
        key: order[key]
        for key in (
            "code",
            "created_at",
            "subtotal",
            "shipping_fee",
            "total",
            "payment_method",
            "payment_state",
            "guide_number",
            "tracking_number",
        )
    }
    result["currency"] = "USD"
    result["delivery_mode"] = "address" if order["address"] else "agency"
    result["status"] = {
        key: order["status"][key] for key in ("slug", "name_es", "name_en", "phase")
    }
    result["items"] = [
        {
            key: line[key]
            for key in (
                "product_name",
                "brand_name",
                "kind",
                "volume_ml",
                "quantity",
                "unit_price",
                "line_total",
            )
        }
        for line in order["items"]
    ]
    result["history"] = [
        {key: event[key] for key in ("name_es", "name_en", "created_at")}
        for event in order["history"]
    ]
    text = "Hola, quisiera consultar mi pedido " + order["code"]
    result["whatsapp_url"] = (
        "https://wa.me/" + number + "?text=" + quote(text, safe="") if number else None
    )
    return result


def private_order(order):
    return {
        key: value
        for key, value in order.items()
        if key not in {"code_hash", "request_hash", "operation_id"}
    }
