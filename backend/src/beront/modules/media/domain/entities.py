from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class MediaAsset:
    id: UUID
    filename: str
    url: str
    name: str
    kind: str
    checksum: str | None
    width: int | None
    height: int | None
    size_bytes: int | None
    uploaded_by: UUID | None
    created_at: datetime
    version: int = 1
