from uuid import uuid4

from beront.modules.commerce.domain.policies import validate_phone
from beront.shared.domain.errors import NotFound


class CommerceService:
    RESOURCES = frozenset({"provinces", "cities", "banks"})

    def __init__(self, uow_factory):
        self.uow_factory = uow_factory

    def settings(self):
        with self.uow_factory() as uow:
            return uow.commerce.settings()

    def whatsapp_number(self):
        settings = self.settings()
        return settings["whatsapp_number"] if settings else ""

    def save_settings(self, data, actor_id, request_id=None):
        validate_phone(data["whatsapp_number"])
        with self.uow_factory() as uow:
            result = uow.commerce.save_settings(data)
            uow.audit(actor_id, "commerce.settings_update", request_id=request_id)
            uow.commit()
            return result

    def listing(self, resource, *, private=False):
        if resource not in self.RESOURCES:
            raise NotFound()
        with self.uow_factory() as uow:
            return uow.commerce.listing(resource, private=private)

    def create(self, resource, data, actor_id, request_id=None):
        if resource not in self.RESOURCES:
            raise NotFound()
        with self.uow_factory() as uow:
            result = uow.commerce.add(resource, {"id": uuid4(), **data})
            uow.audit(actor_id, "commerce." + resource + "_create", result["id"], request_id)
            uow.commit()
            return result

    def update(self, resource, identifier, data, actor_id, request_id=None):
        if resource not in self.RESOURCES:
            raise NotFound()
        with self.uow_factory() as uow:
            current = uow.commerce.get(resource, identifier)
            result = uow.commerce.save(resource, {**current, **data})
            uow.audit(actor_id, "commerce." + resource + "_update", identifier, request_id)
            uow.commit()
            return result

    def options(self):
        with self.uow_factory() as uow:
            settings = uow.commerce.settings()
            return {
                "settings": {
                    key: settings[key] for key in ("whatsapp_number", "terms_es", "terms_en")
                }
                if settings
                else None,
                **{key: uow.commerce.listing(key) for key in self.RESOURCES},
            }
