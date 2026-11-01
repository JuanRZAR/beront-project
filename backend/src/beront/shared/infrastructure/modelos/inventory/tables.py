from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from beront.shared.infrastructure.modelos.base import Base, now


class DecantStockModel(Base):
    __tablename__ = "decant_stock"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    version: Mapped[int] = mapped_column(default=1)
    __mapper_args__ = {"version_id_col": version}
    __table_args__ = (CheckConstraint("amount >= 0", name="nonnegative"),)


class BottleStockModel(Base):
    __tablename__ = "bottle_stock"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    variant_id: Mapped[UUID] = mapped_column(ForeignKey("variants.id"), unique=True)
    amount: Mapped[int] = mapped_column(default=0)
    version: Mapped[int] = mapped_column(default=1)
    __mapper_args__ = {"version_id_col": version}
    __table_args__ = (CheckConstraint("amount >= 0", name="nonnegative"),)


class MovementModel(Base):
    __tablename__ = "stock_movements"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    decant_stock_id: Mapped[UUID | None] = mapped_column(ForeignKey("decant_stock.id"))
    bottle_stock_id: Mapped[UUID | None] = mapped_column(ForeignKey("bottle_stock.id"))
    target_id: Mapped[UUID]
    kind: Mapped[str] = mapped_column(String(12))
    delta: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    balance_after: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    version_after: Mapped[int]
    reason: Mapped[str] = mapped_column(String(300))
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("administrators.id"))
    operation_id: Mapped[UUID] = mapped_column(unique=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    __table_args__ = (
        CheckConstraint(
            "(decant_stock_id IS NOT NULL) <> (bottle_stock_id IS NOT NULL)", name="one_target"
        ),
        CheckConstraint("delta <> 0 AND balance_after >= 0", name="valid_amounts"),
        CheckConstraint(
            "(kind = 'decant' AND decant_stock_id IS NOT NULL) OR (kind = 'full_bottle' AND bottle_stock_id IS NOT NULL AND delta = trunc(delta))",
            name="kind_unit",
        ),
    )
