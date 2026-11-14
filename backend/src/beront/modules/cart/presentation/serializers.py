from beront.shared.domain.values import decimal_text


def quote_data(quote):
    return {
        "currency": quote.currency,
        "items": [
            {
                "variant_id": str(item.variant_id),
                "brand_name": item.brand_name,
                "product_name": item.product_name,
                "kind": item.kind,
                "volume_ml": decimal_text(item.volume_ml),
                "quantity": item.quantity,
                "unit_price": decimal_text(item.unit_price),
                "line_total": decimal_text(item.line_total),
                "product_slug": item.product_slug,
                "image_url": item.image_url,
                "options": [
                    {
                        "variant_id": str(option.variant_id),
                        "volume_ml": decimal_text(option.volume_ml),
                        "unit_price": decimal_text(option.unit_price),
                    }
                    for option in item.options
                ],
            }
            for item in quote.items
        ],
        "total": decimal_text(quote.total),
        "whatsapp_url": quote.whatsapp_url,
        "configuration_error": quote.configuration_error,
    }
