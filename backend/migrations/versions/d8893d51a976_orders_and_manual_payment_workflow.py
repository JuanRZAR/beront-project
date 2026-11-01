"""orders_and_manual_payment_workflow"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from beront.shared.infrastructure.sql_migrations import install_functions

revision: str = "d8893d51a976"
down_revision: str | None = "c128e48e9450"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


SQL_SOURCES = (
    (
        "bd/orders/funciones/v0001/orders_add.sql",
        "19053e249bf8af59340d26e3466876b0e6866d38db1fa9727389f4301ac08c59",
    ),
    (
        "bd/orders/funciones/v0001/orders_get.sql",
        "5d3553a1ac7a49cd210b5eae41a684ccf985466a158e6c11cbc61334c440c162",
    ),
    (
        "bd/orders/funciones/v0001/orders_history_add.sql",
        "7f72f3b76c3410ae2affc9af7e34bf007a1e3290df801d5a03dfd27bc02bad81",
    ),
    (
        "bd/orders/funciones/v0001/orders_list.sql",
        "62bb705bc1d9b97b82b12638a67123bafcd6edba8fcaf0a7cbdfce7ef7d9bf23",
    ),
    (
        "bd/orders/funciones/v0001/orders_operation_lock.sql",
        "c24e15a2daf5ea79598b550135e7198221926cca1fd8bbd1c29277d9fd6bc443",
    ),
    (
        "bd/orders/funciones/v0001/orders_receipt_add.sql",
        "957781b5ebabb4bd9be18973b4f51b56b021d9fd7468c2a8694ab487122a91bc",
    ),
    (
        "bd/orders/funciones/v0001/orders_recovery_add.sql",
        "8e71d176685ac2e53667118a3ca993703128976d6d10b7b3808e4bfe4373945f",
    ),
    (
        "bd/orders/funciones/v0001/orders_recovery_list.sql",
        "6b84462c337e9547ffdbaba91b3fdfbfee89b2ce19e64eb2392ab05d009fb833",
    ),
    (
        "bd/orders/funciones/v0001/orders_recovery_resolve.sql",
        "2cb663abb4f4efb5555aaa42af5342fcae9172b38d1beaf910b12b6eb1fb08fe",
    ),
    (
        "bd/orders/funciones/v0001/orders_save.sql",
        "fd44e6b75822b0017ad562402683561b23defbdaa97cbc2614e60e9570d4a6de",
    ),
    (
        "bd/orders/funciones/v0001/orders_status_add.sql",
        "05c038e1be811303fb077880e60f23106b5ddae3db8ca1cc9db8b4902698d3ef",
    ),
    (
        "bd/orders/funciones/v0001/orders_status_get.sql",
        "7d67e71be9a970113c61d33c0df1054c2416ce6e61d13b68408bfd99538731d5",
    ),
    (
        "bd/orders/funciones/v0001/orders_status_list.sql",
        "60b0f482f203732024f3ff38e524e565b1483608b517ae5256be5fbaa4837ea0",
    ),
    (
        "bd/orders/funciones/v0001/orders_status_save.sql",
        "e74af217fcd51ebf065b3c39e0737a4c44b4390a10766a6f3321fe6add3b723c",
    ),
    (
        "bd/orders/funciones/v0001/orders_transition_add.sql",
        "78e680ec79bb596765ac8b6c8f52637461535e78236c4f4ac05de1deb4f9961d",
    ),
    (
        "bd/orders/funciones/v0001/orders_transition_get.sql",
        "ab69e0ce54aa775927cefea4996e20eade0ebaf5bab9d87096bfde46b9b52bef",
    ),
    (
        "bd/orders/funciones/v0001/orders_transition_list.sql",
        "98024d8bd11011d55f06eb35e721d3ff68142634f54e7854eb8ae6825699a6da",
    ),
    (
        "bd/orders/funciones/v0001/orders_transition_save.sql",
        "90814ec2dc525a79517035d10aadc818028eb82f3edf1dcaf17b2621fb34589d",
    ),
)


def upgrade() -> None:
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
        "order_recoveries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cedula", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["resolved_by"],
            ["administrators.id"],
            name=op.f("fk_order_recoveries_resolved_by_administrators"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_recoveries")),
    )
    op.create_index(
        op.f("ix_order_recoveries_created_at"), "order_recoveries", ["created_at"], unique=False
    )
    op.create_index(
        "uq_order_recoveries_pending",
        "order_recoveries",
        ["cedula"],
        unique=True,
        postgresql_where=sa.text("resolved_at IS NULL"),
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
    install_functions(op.get_bind(), SQL_SOURCES)


def downgrade() -> None:
    for relative, _ in reversed(SQL_SOURCES):
        name = relative.rsplit("/", 1)[1].removesuffix(".sql")
        op.execute(sa.text("DROP FUNCTION beront_api." + name + "(jsonb)"))
    op.drop_index(op.f("ix_order_lines_order_id"), table_name="order_lines")
    op.drop_table("order_lines")
    op.drop_index(op.f("ix_order_receipts_order_id"), table_name="order_receipts")
    op.drop_table("order_receipts")
    op.drop_index(op.f("ix_order_history_order_id"), table_name="order_history")
    op.drop_table("order_history")
    op.drop_index(op.f("ix_orders_status_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_created_at"), table_name="orders")
    op.drop_index(op.f("ix_orders_cedula"), table_name="orders")
    op.drop_table("orders")
    op.drop_table("order_transitions")
    op.drop_index(
        "uq_order_recoveries_pending",
        table_name="order_recoveries",
        postgresql_where=sa.text("resolved_at IS NULL"),
    )
    op.drop_index(op.f("ix_order_recoveries_created_at"), table_name="order_recoveries")
    op.drop_table("order_recoveries")
    op.drop_table("order_statuses")
