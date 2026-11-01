from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from beront.shared.infrastructure.modelos.base import Base


class CategoryModel(Base):
    __tablename__ = "categories"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name_es: Mapped[str] = mapped_column(String(100))
    name_en: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(default=1)


class AudienceModel(Base):
    __tablename__ = "audiences"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name_es: Mapped[str] = mapped_column(String(100))
    name_en: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(default=1)


class PresentationModel(Base):
    __tablename__ = "presentations"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name_es: Mapped[str] = mapped_column(String(100))
    name_en: Mapped[str] = mapped_column(String(100))
    kind: Mapped[str] = mapped_column(String(12))
    volume_ml: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(default=1)
    __table_args__ = (
        UniqueConstraint("kind", "volume_ml", name="uq_presentations_kind_volume"),
        CheckConstraint("kind IN ('decant', 'full_bottle')", name="kind"),
        CheckConstraint("volume_ml > 0", name="positive_volume"),
    )


class BrandModel(Base):
    __tablename__ = "brands"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    normalized_name: Mapped[str] = mapped_column(String(100), unique=True)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id"), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(default=1)
    __mapper_args__ = {"version_id_col": version}


class ProductModel(Base):
    __tablename__ = "products"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    brand_id: Mapped[UUID] = mapped_column(ForeignKey("brands.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    audience: Mapped[str] = mapped_column(String(64), ForeignKey("audiences.slug"), index=True)
    description_es: Mapped[str] = mapped_column(Text, default="")
    description_en: Mapped[str] = mapped_column(Text, default="")
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    sold_out: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(default=1)
    brand: Mapped[BrandModel] = relationship(lazy="selectin")
    variants: Mapped[list["VariantModel"]] = relationship(
        lazy="selectin", order_by="VariantModel.volume_ml"
    )
    images: Mapped[list["ProductImageModel"]] = relationship(
        lazy="selectin", order_by="ProductImageModel.position"
    )
    __mapper_args__ = {"version_id_col": version}


class VariantModel(Base):
    __tablename__ = "variants"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), index=True)
    kind: Mapped[str] = mapped_column(String(12))
    volume_ml: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    sold_out: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(default=1)
    __mapper_args__ = {"version_id_col": version}
    __table_args__ = (
        CheckConstraint("kind IN ('decant', 'full_bottle')", name="kind"),
        CheckConstraint("volume_ml > 0 AND price > 0", name="positive_values"),
        ForeignKeyConstraint(
            ["kind", "volume_ml"],
            ["presentations.kind", "presentations.volume_ml"],
            name="fk_variants_presentation",
        ),
        Index("ix_variants_filter", "kind", "volume_ml", "price"),
    )


class ProductImageModel(Base):
    __tablename__ = "product_images"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), index=True)
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("media_assets.id"), index=True)
    position: Mapped[int] = mapped_column(default=0)
    alt_es: Mapped[str] = mapped_column(String(250), default="")
    alt_en: Mapped[str] = mapped_column(String(250), default="")
    version: Mapped[int] = mapped_column(default=1)
    __mapper_args__ = {"version_id_col": version}
    __table_args__ = (
        CheckConstraint("position >= 0", name="position"),
        UniqueConstraint("product_id", "asset_id", name="uq_product_images_product_asset"),
    )


class ClassificationOptionModel(Base):
    __tablename__ = "classification_options"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    dimension: Mapped[str] = mapped_column(String(16))
    slug: Mapped[str] = mapped_column(String(64))
    name_es: Mapped[str] = mapped_column(String(100))
    name_en: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(default=1)
    __table_args__ = (
        UniqueConstraint("dimension", "slug", name="uq_classification_options_dimension_slug"),
        CheckConstraint("dimension IN ('accord', 'usage', 'profile')", name="dimension"),
    )


class ProductClassificationModel(Base):
    __tablename__ = "product_classifications"
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))
    option_id: Mapped[UUID] = mapped_column(ForeignKey("classification_options.id"), index=True)
    __table_args__ = (
        PrimaryKeyConstraint("product_id", "option_id", name="pk_product_classifications"),
    )
