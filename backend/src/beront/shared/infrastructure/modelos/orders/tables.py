from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from beront.shared.infrastructure.modelos.base import Base, now


class OrderStatusModel(Base):
    __tablename__ = "order_statuses"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name_es: Mapped[str] = mapped_column(String(100))
    name_en: Mapped[str] = mapped_column(String(100))
    phase: Mapped[str] = mapped_column(String(24))
    purpose: Mapped[str | None] = mapped_column(String(20), unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(default=1)
    __table_args__ = (
        CheckConstraint(
            "phase IN ('awaiting_payment','paid','shipped','delivered','cancelled','stock_issue')",
            name="phase",
        ),
        CheckConstraint(
            "purpose IS NULL OR (purpose IN ('bank_transfer','whatsapp') AND phase='awaiting_payment') OR (purpose='stock_issue' AND phase='stock_issue')",
            name="purpose_phase",
        ),
    )


class OrderTransitionModel(Base):
    __tablename__ = "order_transitions"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    from_status_id: Mapped[UUID] = mapped_column(ForeignKey("order_statuses.id"))
    to_status_id: Mapped[UUID] = mapped_column(ForeignKey("order_statuses.id"))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(default=1)
    __table_args__ = (
        UniqueConstraint("from_status_id", "to_status_id", name="uq_order_transitions_pair"),
        CheckConstraint("from_status_id <> to_status_id", name="different_states"),
    )


class OrderModel(Base):
    __tablename__ = "orders"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(40), unique=True)
    code_hash: Mapped[str] = mapped_column(String(64), unique=True)
    operation_id: Mapped[UUID] = mapped_column(unique=True)
    request_hash: Mapped[str] = mapped_column(String(64))
    locale: Mapped[str] = mapped_column(String(2))
    cedula: Mapped[str] = mapped_column(String(20), index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(254))
    city_id: Mapped[UUID] = mapped_column(ForeignKey("cities.id"))
    city_name: Mapped[str] = mapped_column(String(100))
    province_name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(300))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    shipping_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    payment_method: Mapped[str] = mapped_column(String(20))
    bank_snapshot: Mapped[dict | None] = mapped_column(JSONB)
    terms_snapshot: Mapped[dict] = mapped_column(JSONB)
    status_id: Mapped[UUID] = mapped_column(ForeignKey("order_statuses.id"), index=True)
    payment_state: Mapped[str] = mapped_column(String(16), default="pending")
    payment_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[UUID | None] = mapped_column(ForeignKey("administrators.id"))
    guide_number: Mapped[str] = mapped_column(String(100), default="")
    tracking_number: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    version: Mapped[int] = mapped_column(default=1)
    __table_args__ = (
        CheckConstraint("payment_method IN ('bank_transfer','whatsapp')", name="payment_method"),
        CheckConstraint(
            "payment_state IN ('pending','confirmed','stock_issue')", name="payment_state"
        ),
        CheckConstraint(
            "subtotal > 0 AND shipping_fee >= 0 AND total=subtotal+shipping_fee", name="totals"
        ),
        CheckConstraint(
            "(payment_state='confirmed') = (paid_at IS NOT NULL)", name="confirmed_payment"
        ),
        CheckConstraint("locale IN ('es','en')", name="locale"),
    )


class OrderLineModel(Base):
    __tablename__ = "order_lines"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"), index=True)
    variant_id: Mapped[UUID] = mapped_column(ForeignKey("variants.id"))
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))
    product_name: Mapped[str] = mapped_column(String(120))
    brand_name: Mapped[str] = mapped_column(String(100))
    kind: Mapped[str] = mapped_column(String(12))
    volume_ml: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    quantity: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    __table_args__ = (
        UniqueConstraint("order_id", "variant_id", name="uq_order_lines_variant"),
        CheckConstraint(
            "quantity BETWEEN 1 AND 20 AND unit_price>0 AND line_total=quantity*unit_price",
            name="valid_line",
        ),
    )


class OrderHistoryModel(Base):
    __tablename__ = "order_history"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"), index=True)
    status_id: Mapped[UUID] = mapped_column(ForeignKey("order_statuses.id"))
    name_es: Mapped[str] = mapped_column(String(100))
    name_en: Mapped[str] = mapped_column(String(100))
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("administrators.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class OrderReceiptModel(Base):
    __tablename__ = "order_receipts"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"), index=True)
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("media_assets.id"))
    uploaded_by: Mapped[UUID | None] = mapped_column(ForeignKey("administrators.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class OrderRecoveryAttemptModel(Base):
    __tablename__ = "order_recovery_attempts"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    cedula: Mapped[str] = mapped_column(String(20), index=True)
    ip_hash: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
