import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from beront.modules.identity.domain.entities import Administrator, AdminSession
from beront.modules.identity.domain.policies import session_valid, validate_password
from beront.shared.domain.errors import Conflict, NotFound, Unauthorized


class IdentityService:
    def __init__(self, uow_factory, hasher, clock=None):
        self.uow_factory, self.hasher = uow_factory, hasher
        self.clock = clock or (lambda: datetime.now(UTC))

    def create_admin(self, username, password):
        validate_password(password)
        username = username.strip().casefold()
        if not username or len(username) > 100:
            raise ValueError("Usuario inválido.")
        with self.uow_factory() as uow:
            if uow.identity.single():
                raise Conflict("ADMIN_ALREADY_EXISTS", "Ya existe el único administrador.")
            admin = Administrator(uuid4(), username, self.hasher.hash(password))
            uow.identity.add_admin(admin)
            uow.audit(admin.id, "identity.create", admin.id)
            uow.commit()
            return admin

    def reset_password(self, username, password):
        validate_password(password)
        with self.uow_factory() as uow:
            admin = uow.identity.by_username(username.strip().casefold())
            if not admin:
                raise NotFound()
            uow.identity.set_password(admin.id, self.hasher.hash(password))
            uow.identity.revoke_all(admin.id, self.clock())
            uow.audit(admin.id, "identity.password_reset", admin.id)
            uow.commit()

    def login(self, username, password, request_id=None):
        with self.uow_factory() as uow:
            admin = uow.identity.by_username(username.strip().casefold())
            valid = self.hasher.verify(
                admin.password_hash if admin else self.hasher.dummy_hash, password
            )
            if not valid or not admin or not admin.active:
                uow.audit(None, "identity.login_failed", request_id=request_id)
                uow.commit()
                raise Unauthorized()
            token, now = secrets.token_urlsafe(32), self.clock()
            record = AdminSession(
                uuid4(), admin.id, self._hash(token), now, now, now + timedelta(hours=8)
            )
            uow.identity.add_session(record)
            uow.audit(admin.id, "identity.login", record.id, request_id)
            uow.commit()
            return admin, token

    def authenticate(self, token):
        if not token or len(token) > 128:
            raise Unauthorized()
        with self.uow_factory() as uow:
            record = uow.identity.session(self._hash(token))
            now = self.clock()
            if not record or not session_valid(record, now):
                raise Unauthorized()
            admin = uow.identity.administrator(record.admin_id)
            if not admin or not admin.active:
                raise Unauthorized()
            uow.identity.touch(record.id, now)
            uow.commit()
            return admin

    def logout(self, token, request_id=None):
        with self.uow_factory() as uow:
            record = uow.identity.session(self._hash(token))
            if record:
                uow.identity.revoke(record.id, self.clock())
                uow.audit(record.admin_id, "identity.logout", record.id, request_id)
                uow.commit()

    @staticmethod
    def _hash(token):
        return hashlib.sha256(token.encode()).hexdigest()
