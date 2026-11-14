"""initial schema

Revision ID: 0e7393567f81
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from beront.shared.infrastructure.sql_migrations import function_sources, install_functions

revision: str = "0e7393567f81"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "administrators",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("singleton_slot", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "singleton_slot = 1", name=op.f("ck_administrators_single_administrator")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_administrators")),
        sa.UniqueConstraint("singleton_slot", name=op.f("uq_administrators_singleton_slot")),
        sa.UniqueConstraint("username", name=op.f("uq_administrators_username")),
    )
    op.create_table(
        "audiences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name_es", sa.String(length=100), nullable=False),
        sa.Column("name_en", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audiences")),
        sa.UniqueConstraint("slug", name=op.f("uq_audiences_slug")),
    )
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("resource_id", sa.String(length=120), nullable=True),
        sa.Column("request_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_events")),
    )
    op.create_index(
        op.f("ix_audit_events_created_at"), "audit_events", ["created_at"], unique=False
    )
    op.create_table(
        "bank_accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("bank_name", sa.String(length=100), nullable=False),
        sa.Column("account_type", sa.String(length=80), nullable=False),
        sa.Column("account_number", sa.String(length=60), nullable=False),
        sa.Column("holder_name", sa.String(length=160), nullable=False),
        sa.Column("holder_identification", sa.String(length=30), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bank_accounts")),
    )
    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name_es", sa.String(length=100), nullable=False),
        sa.Column("name_en", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
        sa.UniqueConstraint("slug", name=op.f("uq_categories_slug")),
    )
    op.create_table(
        "classification_options",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("dimension", sa.String(length=16), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name_es", sa.String(length=100), nullable=False),
        sa.Column("name_en", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "dimension IN ('accord', 'usage', 'profile')",
            name=op.f("ck_classification_options_dimension"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_classification_options")),
        sa.UniqueConstraint("dimension", "slug", name="uq_classification_options_dimension_slug"),
    )
    op.create_table(
        "order_recovery_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cedula", sa.String(length=20), nullable=False),
        sa.Column("ip_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_recovery_attempts")),
    )
    op.create_index(
        op.f("ix_order_recovery_attempts_cedula"),
        "order_recovery_attempts",
        ["cedula"],
        unique=False,
    )
    op.create_index(
        op.f("ix_order_recovery_attempts_created_at"),
        "order_recovery_attempts",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_order_recovery_attempts_ip_hash"),
        "order_recovery_attempts",
        ["ip_hash"],
        unique=False,
    )
    op.create_table(
        "order_statuses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name_es", sa.String(length=100), nullable=False),
        sa.Column("name_en", sa.String(length=100), nullable=False),
        sa.Column("phase", sa.String(length=24), nullable=False),
        sa.Column("purpose", sa.String(length=20), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "phase IN ('awaiting_payment','paid','shipped','delivered','cancelled','stock_issue')",
            name=op.f("ck_order_statuses_phase"),
        ),
        sa.CheckConstraint(
            "purpose IS NULL OR (purpose IN ('bank_transfer','whatsapp') AND phase='awaiting_payment') OR (purpose='stock_issue' AND phase='stock_issue')",
            name=op.f("ck_order_statuses_purpose_phase"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_statuses")),
        sa.UniqueConstraint("purpose", name=op.f("uq_order_statuses_purpose")),
        sa.UniqueConstraint("slug", name=op.f("uq_order_statuses_slug")),
    )
    op.create_table(
        "presentations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name_es", sa.String(length=100), nullable=False),
        sa.Column("name_en", sa.String(length=100), nullable=False),
        sa.Column("kind", sa.String(length=12), nullable=False),
        sa.Column("volume_ml", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint("kind IN ('decant', 'full_bottle')", name=op.f("ck_presentations_kind")),
        sa.CheckConstraint("volume_ml > 0", name=op.f("ck_presentations_positive_volume")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_presentations")),
        sa.UniqueConstraint("kind", "volume_ml", name="uq_presentations_kind_volume"),
    )
    op.create_table(
        "provinces",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=2), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("mainland", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "code <> '20' OR NOT mainland", name=op.f("ck_provinces_galapagos_excluded")
        ),
        sa.CheckConstraint("code ~ '^[0-9]{2}$'", name=op.f("ck_provinces_province_code")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_provinces")),
        sa.UniqueConstraint("code", name=op.f("uq_provinces_code")),
    )
    op.create_table(
        "store_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("whatsapp_number", sa.String(length=15), nullable=False),
        sa.Column("terms_es", sa.Text(), nullable=False),
        sa.Column("terms_en", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "whatsapp_number = '' OR whatsapp_number ~ '^[1-9][0-9]{7,14}$'",
            name=op.f("ck_store_settings_international_phone"),
        ),
        sa.CheckConstraint("id = 1", name=op.f("ck_store_settings_singleton")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_store_settings")),
    )
    op.create_table(
        "admin_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("admin_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["admin_id"],
            ["administrators.id"],
            name=op.f("fk_admin_sessions_admin_id_administrators"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_admin_sessions")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_admin_sessions_token_hash")),
    )
    op.create_index(
        op.f("ix_admin_sessions_admin_id"), "admin_sessions", ["admin_id"], unique=False
    )
    op.create_table(
        "brands",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("normalized_name", sa.String(length=100), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"], ["categories.id"], name=op.f("fk_brands_category_id_categories")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_brands")),
        sa.UniqueConstraint("name", name=op.f("uq_brands_name")),
        sa.UniqueConstraint("normalized_name", name=op.f("uq_brands_normalized_name")),
    )
    op.create_index(op.f("ix_brands_category_id"), "brands", ["category_id"], unique=False)
    op.create_table(
        "cities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("province_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("shipping_fee", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint("shipping_fee >= 0", name=op.f("ck_cities_nonnegative_fee")),
        sa.ForeignKeyConstraint(
            ["province_id"], ["provinces.id"], name=op.f("fk_cities_province_id_provinces")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cities")),
        sa.UniqueConstraint("province_id", "name", name="uq_cities_province_name"),
    )
    op.create_index(op.f("ix_cities_province_id"), "cities", ["province_id"], unique=False)
    op.create_table(
        "media_assets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("filename", sa.String(length=50), nullable=False),
        sa.Column("url", sa.String(length=250), nullable=False),
        sa.Column("name", sa.String(length=250), nullable=False),
        sa.Column("kind", sa.String(length=12), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("uploaded_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "filename ~ '^[a-f0-9]{32}\\.webp$'", name=op.f("ck_media_assets_generated_filename")
        ),
        sa.CheckConstraint(
            "kind IN ('product', 'receipt')", name=op.f("ck_media_assets_asset_kind")
        ),
        sa.CheckConstraint("url = '/media/' || filename", name=op.f("ck_media_assets_local_url")),
        sa.CheckConstraint(
            "width > 0 AND height > 0 AND size_bytes > 0",
            name=op.f("ck_media_assets_image_dimensions"),
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["administrators.id"],
            name=op.f("fk_media_assets_uploaded_by_administrators"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_media_assets")),
        sa.UniqueConstraint("checksum", "kind", name="uq_media_assets_checksum_kind"),
        sa.UniqueConstraint("filename", name=op.f("uq_media_assets_filename")),
        sa.UniqueConstraint("url", name=op.f("uq_media_assets_url")),
    )
    op.create_index(
        op.f("ix_media_assets_created_at"), "media_assets", ["created_at"], unique=False
    )
    op.create_table(
        "order_transitions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("from_status_id", sa.Uuid(), nullable=False),
        sa.Column("to_status_id", sa.Uuid(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "from_status_id <> to_status_id", name=op.f("ck_order_transitions_different_states")
        ),
        sa.ForeignKeyConstraint(
            ["from_status_id"],
            ["order_statuses.id"],
            name=op.f("fk_order_transitions_from_status_id_order_statuses"),
        ),
        sa.ForeignKeyConstraint(
            ["to_status_id"],
            ["order_statuses.id"],
            name=op.f("fk_order_transitions_to_status_id_order_statuses"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_transitions")),
        sa.UniqueConstraint("from_status_id", "to_status_id", name="uq_order_transitions_pair"),
    )
    op.create_table(
        "orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("locale", sa.String(length=2), nullable=False),
        sa.Column("cedula", sa.String(length=20), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("city_id", sa.Uuid(), nullable=False),
        sa.Column("city_name", sa.String(length=100), nullable=False),
        sa.Column("province_name", sa.String(length=100), nullable=False),
        sa.Column("address", sa.String(length=300), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("shipping_fee", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("payment_method", sa.String(length=20), nullable=False),
        sa.Column("bank_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("terms_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status_id", sa.Uuid(), nullable=False),
        sa.Column("payment_state", sa.String(length=16), nullable=False),
        sa.Column("payment_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.Uuid(), nullable=True),
        sa.Column("guide_number", sa.String(length=100), nullable=False),
        sa.Column("tracking_number", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "(payment_state='confirmed') = (paid_at IS NOT NULL)",
            name=op.f("ck_orders_confirmed_payment"),
        ),
        sa.CheckConstraint("locale IN ('es','en')", name=op.f("ck_orders_locale")),
        sa.CheckConstraint(
            "payment_method IN ('bank_transfer','whatsapp')", name=op.f("ck_orders_payment_method")
        ),
        sa.CheckConstraint(
            "payment_state IN ('pending','confirmed','stock_issue')",
            name=op.f("ck_orders_payment_state"),
        ),
        sa.CheckConstraint(
            "subtotal > 0 AND shipping_fee >= 0 AND total=subtotal+shipping_fee",
            name=op.f("ck_orders_totals"),
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"],
            ["administrators.id"],
            name=op.f("fk_orders_approved_by_administrators"),
        ),
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"], name=op.f("fk_orders_city_id_cities")),
        sa.ForeignKeyConstraint(
            ["status_id"], ["order_statuses.id"], name=op.f("fk_orders_status_id_order_statuses")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders")),
        sa.UniqueConstraint("code", name=op.f("uq_orders_code")),
        sa.UniqueConstraint("code_hash", name=op.f("uq_orders_code_hash")),
        sa.UniqueConstraint("operation_id", name=op.f("uq_orders_operation_id")),
    )
    op.create_index(op.f("ix_orders_cedula"), "orders", ["cedula"], unique=False)
    op.create_index(op.f("ix_orders_created_at"), "orders", ["created_at"], unique=False)
    op.create_index(op.f("ix_orders_status_id"), "orders", ["status_id"], unique=False)
    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("brand_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("audience", sa.String(length=64), nullable=False),
        sa.Column("description_es", sa.Text(), nullable=False),
        sa.Column("description_en", sa.Text(), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False),
        sa.Column("archived", sa.Boolean(), nullable=False),
        sa.Column("sold_out", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["audience"], ["audiences.slug"], name=op.f("fk_products_audience_audiences")
        ),
        sa.ForeignKeyConstraint(
            ["brand_id"], ["brands.id"], name=op.f("fk_products_brand_id_brands")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_products")),
        sa.UniqueConstraint("slug", name=op.f("uq_products_slug")),
    )
    op.create_index(op.f("ix_products_audience"), "products", ["audience"], unique=False)
    op.create_index(op.f("ix_products_brand_id"), "products", ["brand_id"], unique=False)
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)
    op.create_table(
        "decant_stock",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint("amount >= 0", name=op.f("ck_decant_stock_nonnegative")),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], name=op.f("fk_decant_stock_product_id_products")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_decant_stock")),
        sa.UniqueConstraint("product_id", name=op.f("uq_decant_stock_product_id")),
    )
    op.create_table(
        "order_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("status_id", sa.Uuid(), nullable=False),
        sa.Column("name_es", sa.String(length=100), nullable=False),
        sa.Column("name_en", sa.String(length=100), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["administrators.id"],
            name=op.f("fk_order_history_actor_id_administrators"),
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], name=op.f("fk_order_history_order_id_orders")
        ),
        sa.ForeignKeyConstraint(
            ["status_id"],
            ["order_statuses.id"],
            name=op.f("fk_order_history_status_id_order_statuses"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_history")),
    )
    op.create_index(op.f("ix_order_history_order_id"), "order_history", ["order_id"], unique=False)
    op.create_table(
        "order_receipts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("asset_id", sa.Uuid(), nullable=False),
        sa.Column("uploaded_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["asset_id"], ["media_assets.id"], name=op.f("fk_order_receipts_asset_id_media_assets")
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], name=op.f("fk_order_receipts_order_id_orders")
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["administrators.id"],
            name=op.f("fk_order_receipts_uploaded_by_administrators"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_receipts")),
    )
    op.create_index(
        op.f("ix_order_receipts_order_id"), "order_receipts", ["order_id"], unique=False
    )
    op.create_table(
        "product_classifications",
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("option_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["option_id"],
            ["classification_options.id"],
            name=op.f("fk_product_classifications_option_id_classification_options"),
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_product_classifications_product_id_products"),
        ),
        sa.PrimaryKeyConstraint("product_id", "option_id", name="pk_product_classifications"),
    )
    op.create_index(
        op.f("ix_product_classifications_option_id"),
        "product_classifications",
        ["option_id"],
        unique=False,
    )
    op.create_table(
        "product_images",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("asset_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("alt_es", sa.String(length=250), nullable=False),
        sa.Column("alt_en", sa.String(length=250), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint("position >= 0", name=op.f("ck_product_images_position")),
        sa.ForeignKeyConstraint(
            ["asset_id"], ["media_assets.id"], name=op.f("fk_product_images_asset_id_media_assets")
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], name=op.f("fk_product_images_product_id_products")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_images")),
        sa.UniqueConstraint("product_id", "asset_id", name="uq_product_images_product_asset"),
    )
    op.create_index(
        op.f("ix_product_images_asset_id"), "product_images", ["asset_id"], unique=False
    )
    op.create_index(
        op.f("ix_product_images_product_id"), "product_images", ["product_id"], unique=False
    )
    op.create_table(
        "variants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=12), nullable=False),
        sa.Column("volume_ml", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("sold_out", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint("kind IN ('decant', 'full_bottle')", name=op.f("ck_variants_kind")),
        sa.CheckConstraint("volume_ml > 0 AND price > 0", name=op.f("ck_variants_positive_values")),
        sa.ForeignKeyConstraint(
            ["kind", "volume_ml"],
            ["presentations.kind", "presentations.volume_ml"],
            name="fk_variants_presentation",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], name=op.f("fk_variants_product_id_products")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_variants")),
    )
    op.create_index("ix_variants_filter", "variants", ["kind", "volume_ml", "price"], unique=False)
    op.create_index(op.f("ix_variants_product_id"), "variants", ["product_id"], unique=False)
    op.create_table(
        "bottle_stock",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("variant_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint("amount >= 0", name=op.f("ck_bottle_stock_nonnegative")),
        sa.ForeignKeyConstraint(
            ["variant_id"], ["variants.id"], name=op.f("fk_bottle_stock_variant_id_variants")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bottle_stock")),
        sa.UniqueConstraint("variant_id", name=op.f("uq_bottle_stock_variant_id")),
    )
    op.create_table(
        "order_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("variant_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("product_name", sa.String(length=120), nullable=False),
        sa.Column("brand_name", sa.String(length=100), nullable=False),
        sa.Column("kind", sa.String(length=12), nullable=False),
        sa.Column("volume_ml", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("line_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.CheckConstraint(
            "quantity BETWEEN 1 AND 20 AND unit_price>0 AND line_total=quantity*unit_price",
            name=op.f("ck_order_lines_valid_line"),
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], name=op.f("fk_order_lines_order_id_orders")
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], name=op.f("fk_order_lines_product_id_products")
        ),
        sa.ForeignKeyConstraint(
            ["variant_id"], ["variants.id"], name=op.f("fk_order_lines_variant_id_variants")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_lines")),
        sa.UniqueConstraint("order_id", "variant_id", name="uq_order_lines_variant"),
    )
    op.create_index(op.f("ix_order_lines_order_id"), "order_lines", ["order_id"], unique=False)
    op.create_table(
        "stock_movements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decant_stock_id", sa.Uuid(), nullable=True),
        sa.Column("bottle_stock_id", sa.Uuid(), nullable=True),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=12), nullable=False),
        sa.Column("delta", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("balance_after", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("version_after", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=300), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "(kind = 'decant' AND decant_stock_id IS NOT NULL) OR (kind = 'full_bottle' AND bottle_stock_id IS NOT NULL AND delta = trunc(delta))",
            name=op.f("ck_stock_movements_kind_unit"),
        ),
        sa.CheckConstraint(
            "(decant_stock_id IS NOT NULL) <> (bottle_stock_id IS NOT NULL)",
            name=op.f("ck_stock_movements_one_target"),
        ),
        sa.CheckConstraint(
            "delta <> 0 AND balance_after >= 0", name=op.f("ck_stock_movements_valid_amounts")
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["administrators.id"],
            name=op.f("fk_stock_movements_actor_id_administrators"),
        ),
        sa.ForeignKeyConstraint(
            ["bottle_stock_id"],
            ["bottle_stock.id"],
            name=op.f("fk_stock_movements_bottle_stock_id_bottle_stock"),
        ),
        sa.ForeignKeyConstraint(
            ["decant_stock_id"],
            ["decant_stock.id"],
            name=op.f("fk_stock_movements_decant_stock_id_decant_stock"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stock_movements")),
        sa.UniqueConstraint("operation_id", name=op.f("uq_stock_movements_operation_id")),
    )
    op.create_index(
        op.f("ix_stock_movements_created_at"), "stock_movements", ["created_at"], unique=False
    )
    op.execute("CREATE SCHEMA beront_api")
    op.execute("REVOKE ALL ON SCHEMA beront_api FROM PUBLIC")
    install_functions(op.get_bind(), function_sources())


def downgrade() -> None:
    op.execute("DROP SCHEMA beront_api CASCADE")
    op.drop_index(op.f("ix_stock_movements_created_at"), table_name="stock_movements")
    op.drop_table("stock_movements")
    op.drop_index(op.f("ix_order_lines_order_id"), table_name="order_lines")
    op.drop_table("order_lines")
    op.drop_table("bottle_stock")
    op.drop_index(op.f("ix_variants_product_id"), table_name="variants")
    op.drop_index("ix_variants_filter", table_name="variants")
    op.drop_table("variants")
    op.drop_index(op.f("ix_product_images_product_id"), table_name="product_images")
    op.drop_index(op.f("ix_product_images_asset_id"), table_name="product_images")
    op.drop_table("product_images")
    op.drop_index(
        op.f("ix_product_classifications_option_id"), table_name="product_classifications"
    )
    op.drop_table("product_classifications")
    op.drop_index(op.f("ix_order_receipts_order_id"), table_name="order_receipts")
    op.drop_table("order_receipts")
    op.drop_index(op.f("ix_order_history_order_id"), table_name="order_history")
    op.drop_table("order_history")
    op.drop_table("decant_stock")
    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_index(op.f("ix_products_brand_id"), table_name="products")
    op.drop_index(op.f("ix_products_audience"), table_name="products")
    op.drop_table("products")
    op.drop_index(op.f("ix_orders_status_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_created_at"), table_name="orders")
    op.drop_index(op.f("ix_orders_cedula"), table_name="orders")
    op.drop_table("orders")
    op.drop_table("order_transitions")
    op.drop_index(op.f("ix_media_assets_created_at"), table_name="media_assets")
    op.drop_table("media_assets")
    op.drop_index(op.f("ix_cities_province_id"), table_name="cities")
    op.drop_table("cities")
    op.drop_index(op.f("ix_brands_category_id"), table_name="brands")
    op.drop_table("brands")
    op.drop_index(op.f("ix_admin_sessions_admin_id"), table_name="admin_sessions")
    op.drop_table("admin_sessions")
    op.drop_table("store_settings")
    op.drop_table("provinces")
    op.drop_table("presentations")
    op.drop_table("order_statuses")
    op.drop_index(op.f("ix_order_recovery_attempts_ip_hash"), table_name="order_recovery_attempts")
    op.drop_index(
        op.f("ix_order_recovery_attempts_created_at"), table_name="order_recovery_attempts"
    )
    op.drop_index(op.f("ix_order_recovery_attempts_cedula"), table_name="order_recovery_attempts")
    op.drop_table("order_recovery_attempts")
    op.drop_table("classification_options")
    op.drop_table("categories")
    op.drop_table("bank_accounts")
    op.drop_index(op.f("ix_audit_events_created_at"), table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_table("audiences")
    op.drop_table("administrators")
