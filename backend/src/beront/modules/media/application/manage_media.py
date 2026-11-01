import logging


class MediaService:
    def __init__(self, uow_factory, storage):
        self.uow_factory, self.storage = uow_factory, storage

    def listing(self, q="", page=1, page_size=24):
        with self.uow_factory() as uow:
            return uow.media.listing(q, page, page_size)

    def upload(self, stream, name, actor_id, request_id=None):
        filename = self.storage.save(stream)
        try:
            data = {
                **self.storage.describe(filename),
                "name": name,
                "kind": "product",
                "uploaded_by": actor_id,
            }
            with self.uow_factory() as uow:
                asset, created = uow.media.register(data)
                if created:
                    uow.audit(actor_id, "media.upload", asset.id, request_id)
                uow.commit()
        except Exception:
            self.storage.delete(filename)
            raise
        if not created:
            self.storage.delete(filename)
        return asset, created

    def update(self, identifier, data, actor_id, request_id=None):
        with self.uow_factory() as uow:
            asset = uow.media.update(identifier, data)
            uow.audit(actor_id, "media.update", identifier, request_id)
            uow.commit()
            return asset

    def delete(self, identifier, version, actor_id, request_id=None):
        with self.uow_factory() as uow:
            asset = uow.media.delete(identifier, version)
            uow.audit(actor_id, "media.delete", identifier, request_id)
            uow.commit()
        try:
            self.storage.delete(asset.filename)
        except OSError:
            logging.getLogger("beront").error(
                "media.cleanup_failed", extra={"request_id": request_id}
            )

    def visible(self, filename, *, private=False):
        with self.uow_factory() as uow:
            return uow.media.visible(filename, private=private)
