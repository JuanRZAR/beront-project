from typing import Protocol


class WhatsAppLink(Protocol):
    def build(self, lines, locale: str) -> str | None: ...
