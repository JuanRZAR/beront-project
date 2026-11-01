from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from beront.shared.infrastructure.modelos.base import Base


class StoreSettingsModel(Base):
    __tablename__ = "store_settings"
    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    whatsapp_number: Mapped[str] = mapped_column(String(15))
    terms_es: Mapped[str] = mapped_column(Text)
    terms_en: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(default=1)
    __table_args__ = (
        CheckConstraint("id = 1", name="singleton"),
        CheckConstraint(
            "whatsapp_number = '' OR whatsapp_number ~ '^[1-9][0-9]{7,14}$'",
            name="international_phone",
        ),
    )


class ProvinceModel(Base):
    __tablename__ = "provinces"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(2), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    mainland: Mapped[bool] = mapped_column(Boolean)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(default=1)
    __table_args__ = (
        CheckConstraint("code ~ '^[0-9]{2}$'", name="province_code"),
        CheckConstraint("code <> '20' OR NOT mainland", name="galapagos_excluded"),
    )


class CityModel(Base):
    __tablename__ = "cities"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    province_id: Mapped[UUID] = mapped_column(ForeignKey("provinces.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    shipping_fee: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(default=1)
    __table_args__ = (
        UniqueConstraint("province_id", "name", name="uq_cities_province_name"),
        CheckConstraint("shipping_fee >= 0", name="nonnegative_fee"),
    )


class BankAccountModel(Base):
    __tablename__ = "bank_accounts"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    bank_name: Mapped[str] = mapped_column(String(100))
    account_type: Mapped[str] = mapped_column(String(80))
    account_number: Mapped[str] = mapped_column(String(60))
    holder_name: Mapped[str] = mapped_column(String(160))
    holder_identification: Mapped[str] = mapped_column(String(30))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(default=1)
