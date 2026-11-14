from decimal import Decimal
from urllib.parse import quote


class WhatsAppLinkBuilder:
    def __init__(self, number):
        self.number = number

    def build(self, lines, locale):
        number = self.number() if callable(self.number) else self.number
        if not number:
            return None
        english = locale == "en"
        text = ["*BÉRONT*", "Product summary" if english else "Resumen de productos", ""]
        for index, item in enumerate(lines, start=1):
            kind = (
                ("Full bottle" if english else "Perfume completo")
                if item.kind == "full_bottle"
                else "Decant"
            )
            name = " ".join(f"{item.brand_name} — {item.product_name}".split())
            volume = format(item.volume_ml.normalize(), "f")
            text.extend(
                [
                    f"*{index}. {name}*",
                    f"{'Presentation' if english else 'Presentación'}: {kind} · {volume} ml",
                    f"{'Quantity' if english else 'Cantidad'}: {item.quantity}",
                    f"{'Unit price' if english else 'Precio unitario'}: USD {item.unit_price:.2f}",
                    f"Subtotal: USD {item.line_total:.2f}",
                    "",
                ]
            )
        total = sum((item.line_total for item in lines), Decimal("0.00"))
        text.append(f"*Total: USD {total:.2f}*")
        text.append("Shipping not included." if english else "No incluye envío.")
        text.append("")
        text.append(
            "Availability and shipping to be confirmed."
            if english
            else "Disponibilidad y envío por confirmar."
        )
        return f"https://wa.me/{number}?text={quote(chr(10).join(text), safe='')}"
