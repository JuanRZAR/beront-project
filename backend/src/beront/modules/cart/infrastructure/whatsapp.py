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
        text = ["BÉRONT", "Product summary" if english else "Resumen de productos"]
        for item in lines:
            kind = (
                ("Full bottle" if english else "Perfume completo")
                if item.kind == "full_bottle"
                else "Decant"
            )
            name = " ".join(f"{item.brand_name} — {item.product_name}".split())
            text.append(
                f"{name} | {kind} {item.volume_ml:g} ml | {item.quantity} x USD {item.unit_price:.2f} = USD {item.line_total:.2f}"
            )
        total = sum((item.line_total for item in lines), Decimal("0.00"))
        text.append(f"Total: USD {total:.2f}")
        return f"https://wa.me/{number}?text={quote(chr(10).join(text), safe='')}"
