from uuid import NAMESPACE_URL, uuid5

from beront.modules.commerce.domain.policies import validate_message
from beront.shared.domain.errors import DomainError, NotFound


def default_messages():
    rows = [
        (
            "welcome",
            "bottle",
            "none",
            "/catalog/decants",
            "/catalog/full-bottles",
            (
                "Bienvenido",
                "Una esencia. Tu forma de",
                "descubrirla.",
                "Encuentra tu próximo perfume en decants o elige su presentación completa.",
                "Ver decants",
                "Ver perfumes completos",
            ),
            (
                "Welcome",
                "One essence. Your way to",
                "discover it.",
                "Find your next fragrance as decants or pick its full presentation.",
                "See decants",
                "See full bottles",
            ),
            ["lattafa-fakhar-black", "valentino-uomo-born-in-roma-intense", "xerjoff-erba-pura"],
        ),
        (
            "decants",
            "bottle",
            "decant",
            "/catalog/decants",
            "",
            (
                "Decants",
                "Prueba antes de",
                "enamorarte.",
                "Elige los mililitros que quieras llevar.",
                "Ver decants",
                "",
            ),
            (
                "Decants",
                "Try it before you",
                "fall for it.",
                "Pick the millilitres you want to take.",
                "See decants",
                "",
            ),
            ["lattafa-yara", "jean-paul-gaultier-le-male-le-parfum", "rasasi-hawas-tropical"],
        ),
        (
            "full-bottles",
            "bottle",
            "full_bottle",
            "/catalog/full-bottles",
            "",
            (
                "Perfumes completos",
                "Cada frasco,",
                "a tu alcance.",
                "Elige tu próxima fragancia en su presentación completa.",
                "Ver perfumes completos",
                "",
            ),
            (
                "Full bottles",
                "Every bottle,",
                "within reach.",
                "Pick your next fragrance in its full presentation.",
                "See full bottles",
                "",
            ),
            ["afnan-9pm", "lattafa-khamrah-waha", "xerjoff-erba-gold"],
        ),
        (
            "shipping",
            "truck",
            "none",
            "/orders",
            "",
            (
                "Envíos",
                "Llegamos a todo el",
                "Ecuador continental.",
                "Envíos con Servientrega. Galápagos e islas excluidos. Todos los precios en USD.",
                "Consultar mi pedido",
                "",
            ),
            (
                "Shipping",
                "We reach all of",
                "mainland Ecuador.",
                "Shipping with Servientrega. Galapagos and islands excluded. All prices in USD.",
                "Look up my order",
                "",
            ),
            [],
        ),
        (
            "payment",
            "whatsapp",
            "none",
            "/checkout",
            "/orders",
            (
                "Compra a tu manera",
                "Transferencia o",
                "WhatsApp.",
                "Paga por transferencia con revisión del comprobante o coordina el pago por WhatsApp. Sigue tu pedido con tu código.",
                "Ver carrito",
                "Mi pedido",
            ),
            (
                "Buy your way",
                "Bank transfer or",
                "WhatsApp.",
                "Pay by bank transfer with receipt review, or arrange payment on WhatsApp. Track your order with your code.",
                "See cart",
                "My order",
            ),
            [],
        ),
        (
            "promotion",
            "tag",
            "none",
            "/catalog/decants",
            "",
            (
                "Promoción",
                "Tu promoción",
                "destacada aquí.",
                "El propietario define texto, imagen, enlace y fechas antes de publicarla.",
                "Ver decants",
                "",
            ),
            (
                "Promotion",
                "Your featured promotion",
                "goes here.",
                "The owner sets text, image, link and dates before publishing.",
                "See decants",
                "",
            ),
            [],
        ),
    ]
    fields = ("eyebrow", "title", "emphasis", "body", "primary_label", "secondary_label")
    for position, (slug, icon, kind, primary, secondary, es, en, products) in enumerate(rows):
        yield {
            "id": uuid5(NAMESPACE_URL, "beront:home:" + slug),
            "slug": slug,
            "content": {
                "es": dict(zip(fields, es, strict=True)),
                "en": dict(zip(fields, en, strict=True)),
            },
            "icon": icon,
            "stats_kind": kind,
            "primary_path": primary,
            "secondary_path": secondary,
            "position": position,
            "active": slug != "promotion",
            "starts_at": None,
            "ends_at": None,
            "image_ids": [],
            "products": products,
        }


class SeedHomeMessages:
    def __init__(self, uow_factory):
        self.uow_factory = uow_factory

    def execute(self):
        with self.uow_factory() as uow:
            owner = uow.identity.single()
            if not owner or not owner.active:
                raise DomainError("ADMIN_REQUIRED", "Se necesita un administrador activo.")
            existing = {row["id"] for row in uow.commerce.messages(private=True)}
            created = 0
            for row in default_messages():
                products = row.pop("products")
                if str(row["id"]) in existing:
                    continue
                for slug in products:
                    try:
                        product = uow.catalog.by_slug(slug)
                    except NotFound:
                        continue
                    if product.visible and product.images:
                        row["image_ids"].append(product.images[0].asset_id)
                validate_message(row)
                uow.commerce.add_message(row)
                uow.audit(owner.id, "commerce.message_create", row["id"])
                created += 1
            uow.commit()
            return created
