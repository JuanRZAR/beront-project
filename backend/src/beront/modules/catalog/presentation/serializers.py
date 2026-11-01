from beront.shared.domain.values import decimal_text


def brand_data(brand):
    return {
        "id": str(brand.id),
        "name": brand.name,
        "active": brand.active,
        "version": brand.version,
        "category_id": str(brand.category_id),
    }


def variant_data(variant, *, private=False, available=False):
    result = {
        "id": str(variant.id),
        "kind": variant.kind,
        "volume_ml": decimal_text(variant.volume_ml),
        "price": decimal_text(variant.price),
        "available": available,
    }
    if private:
        result.update(
            product_id=str(variant.product_id),
            active=variant.active,
            sold_out=variant.sold_out,
            version=variant.version,
        )
    return result


def image_data(image, *, private=False):
    result = {
        "id": str(image.id),
        "url": image.url,
        "position": image.position,
        "alt_es": image.alt_es,
        "alt_en": image.alt_en,
    }
    if private:
        result["version"] = image.version
        result["asset_id"] = str(image.asset_id)
    return result


def product_data(product, *, private=False, locale="es", view=None):
    description_locale = "en" if locale == "en" and product.description_en else "es"
    variants = view.variants if view else product.variants
    availability = view.availability if view else {}
    result = {
        "id": str(product.id),
        "name": product.name,
        "slug": product.slug,
        "brand": {"id": str(product.brand_id), "name": product.brand_name},
        "audience": product.audience,
        "classifications": product.classifications,
        "accords": product.accords,
        "usages": product.usages,
        "profiles": product.profiles,
        "description": product.description_en
        if description_locale == "en"
        else product.description_es,
        "description_locale": description_locale,
        "variants": [
            variant_data(v, private=private, available=availability.get(v.id, False))
            for v in variants
        ],
        "images": [image_data(i, private=private) for i in product.images],
        "available": any(availability.get(v.id, False) for v in variants),
        "price_from": decimal_text(min(v.price for v in variants)) if variants else None,
        "currency": "USD",
    }
    if private:
        result.update(
            version=product.version,
            published=product.published,
            archived=product.archived,
            sold_out=product.sold_out,
            description_es=product.description_es,
            description_en=product.description_en,
        )
    return result
