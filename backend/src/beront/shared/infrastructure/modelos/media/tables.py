from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from beront.shared.infrastructure.modelos.base import Base, now


class MediaAssetModel(Base):
    __tablename__ = "media_assets"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    filename: Mapped[str] = mapped_column(String(50), unique=True)
    url: Mapped[str] = mapped_column(String(250), unique=True)
    name: Mapped[str] = mapped_column(String(250), default="")
    kind: Mapped[str] = mapped_column(String(12), default="product")
    checksum: Mapped[str | None] = mapped_column(String(64))
    width: Mapped[int | None]
    height: Mapped[int | None]
    size_bytes: Mapped[int | None]
    uploaded_by: Mapped[UUID | None] = mapped_column(ForeignKey("administrators.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    version: Mapped[int] = mapped_column(default=1)
    __table_args__ = (
        UniqueConstraint("checksum", "kind", name="uq_media_assets_checksum_kind"),
        CheckConstraint("filename ~ '^[a-f0-9]{32}\\.webp$'", name="generated_filename"),
        CheckConstraint("url = '/media/' || filename", name="local_url"),
        CheckConstraint("kind IN ('product', 'receipt')", name="asset_kind"),
        CheckConstraint("width > 0 AND height > 0 AND size_bytes > 0", name="image_dimensions"),
    )
