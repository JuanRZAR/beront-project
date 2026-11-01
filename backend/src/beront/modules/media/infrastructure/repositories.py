from datetime import datetime
from uuid import UUID

from beront.modules.media.domain.entities import MediaAsset
from beront.shared.infrastructure.pg_call import require_record


def to_asset(row):
    data = {key: row[key] for key in MediaAsset.__dataclass_fields__}
    data["id"] = UUID(data["id"])
    data["uploaded_by"] = UUID(data["uploaded_by"]) if data["uploaded_by"] else None
    data["created_at"] = datetime.fromisoformat(data["created_at"])
    return MediaAsset(**data)


class SqlMediaRepository:
    def __init__(self, pg):
        self.pg = pg

    def asset(self, identifier):
        return to_asset(require_record(self.pg.call("media_get", {"id": identifier})))

    def register(self, data):
        result = self.pg.call("media_register", data)
        return to_asset(result["asset"]), result["created"]

    def listing(self, q, page, page_size):
        result = self.pg.call("media_list", {"q": q, "page": page, "page_size": page_size})
        return [to_asset(row) for row in result["items"]], result["total"]

    def update(self, identifier, data):
        return to_asset(self.pg.call("media_update", {**data, "id": identifier}))

    def delete(self, identifier, version):
        return to_asset(self.pg.call("media_delete", {"id": identifier, "version": version}))

    def visible(self, filename, *, private=False):
        return to_asset(
            require_record(
                self.pg.call("media_visible", {"filename": filename, "private": private})
            )
        )
