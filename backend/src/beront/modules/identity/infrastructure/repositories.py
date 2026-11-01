from datetime import datetime
from uuid import UUID

from beront.modules.identity.domain.entities import Administrator, AdminSession


class SqlIdentityRepository:
    def __init__(self, pg):
        self.pg = pg

    @staticmethod
    def _admin(row):
        return (
            Administrator(UUID(row["id"]), row["username"], row["password_hash"], row["active"])
            if row
            else None
        )

    def single(self):
        return self._admin(self.pg.call("identity_admin_get", {"single": True}))

    def by_username(self, username):
        return self._admin(self.pg.call("identity_admin_get", {"username": username}))

    def administrator(self, identifier):
        return self._admin(self.pg.call("identity_admin_get", {"id": identifier}))

    def add_admin(self, administrator):
        self.pg.call("identity_admin_create", vars(administrator))

    def set_password(self, identifier, password_hash):
        self.pg.call("identity_password_set", {"id": identifier, "password_hash": password_hash})

    def session(self, token_hash):
        row = self.pg.call("identity_session_get", {"token_hash": token_hash})
        if not row:
            return None
        values = {key: row[key] for key in AdminSession.__dataclass_fields__}
        for key in ("id", "admin_id"):
            values[key] = UUID(values[key])
        for key in ("created_at", "last_seen_at", "expires_at", "revoked_at"):
            values[key] = datetime.fromisoformat(values[key]) if values[key] else None
        return AdminSession(**values)

    def add_session(self, session):
        self.pg.call("identity_session_add", vars(session))

    def touch(self, identifier, now):
        self.pg.call("identity_session_touch", {"id": identifier, "now": now})

    def revoke(self, identifier, now):
        self.pg.call("identity_session_revoke", {"id": identifier, "now": now})

    def revoke_all(self, admin_id, now):
        self.pg.call("identity_sessions_revoke_all", {"admin_id": admin_id, "now": now})
