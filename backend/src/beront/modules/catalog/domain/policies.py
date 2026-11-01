from beront.shared.domain.errors import Conflict, DomainError


def ensure_version(entity, expected):
    if entity.version != expected:
        raise Conflict()


def ensure_publishable(product):
    if (
        product.published
        and not product.archived
        and not any(v.active and v.presentation_active for v in product.variants)
    ):
        raise DomainError(
            "PRODUCT_NOT_READY", "Añade al menos una presentación activa para publicar."
        )
