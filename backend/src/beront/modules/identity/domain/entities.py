from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Administrator:
    id: UUID
    username: str
    password_hash: str = field(repr=False)
    active: bool = True


@dataclass
class AdminSession:
    id: UUID
    admin_id: UUID
    token_hash: str = field(repr=False)
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None
