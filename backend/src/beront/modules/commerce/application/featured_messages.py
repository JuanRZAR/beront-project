from datetime import UTC, datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from beront.modules.commerce.domain.daily_selection import daily_choice
from beront.modules.commerce.domain.policies import validate_message

DAILY_MESSAGES = frozenset({"welcome", "decants", "full-bottles"})
DAILY_CATEGORIES = ("arabic", "designer", "niche")


class FeaturedMessages:
    def __init__(self, uow_factory, *, now=None):
        self.uow_factory = uow_factory
        self.now = now or (lambda: datetime.now(UTC))

    def listing(self, *, private=False):
        with self.uow_factory() as uow:
            messages = uow.commerce.messages(private=private)
            if private or not any(row["slug"] in DAILY_MESSAGES for row in messages):
                return messages
            products, offset = [], 0
            while True:
                batch = uow.catalog.candidates({}, offset=offset, limit=100)
                products.extend(product for product in batch if product.images)
                if len(batch) < 100:
                    break
                offset += len(batch)
            day = self.now().astimezone(ZoneInfo("America/Guayaquil")).date()
            for row in messages:
                if row["slug"] not in DAILY_MESSAGES:
                    continue
                images, selected = [], set()
                for category in DAILY_CATEGORIES:
                    candidates = {
                        str(product.id): product
                        for product in products
                        if category in product.classifications and product.id not in selected
                    }
                    chosen = daily_choice(list(candidates), day, f"home:{row['slug']}:{category}")
                    if chosen is None:
                        images = []
                        break
                    product = candidates[chosen]
                    selected.add(product.id)
                    image = min(product.images, key=lambda item: item.position)
                    images.append(
                        {
                            "id": str(image.asset_id),
                            "url": image.url,
                            "name": f"{product.brand_name} {product.name}",
                        }
                    )
                row["images"] = images
                row["image_ids"] = [image["id"] for image in images]
            return messages

    def create(self, data, actor_id, request_id=None):
        validate_message(data)
        with self.uow_factory() as uow:
            result = uow.commerce.add_message({"id": uuid4(), **data})
            uow.audit(actor_id, "commerce.message_create", result["id"], request_id)
            uow.commit()
            return result

    def save(self, identifier, data, actor_id, request_id=None):
        validate_message(data)
        with self.uow_factory() as uow:
            result = uow.commerce.save_message({"id": identifier, **data})
            uow.audit(actor_id, "commerce.message_update", identifier, request_id)
            uow.commit()
            return result
