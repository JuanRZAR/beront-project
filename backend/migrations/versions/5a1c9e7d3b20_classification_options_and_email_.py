"""Classification options for perfumes and e-mail code recovery with cooldown."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from beront.shared.infrastructure.sql_migrations import install_functions

SQL_SOURCES = (
    (
        "bd/catalog/funciones/v0004/catalog_option_list.sql",
        "73b05129b047b984d7ace517288bedff36727bfb334cbc5fc506e207be0f9731",
    ),
    (
        "bd/catalog/funciones/v0004/catalog_option_get.sql",
        "c2bb78f4d838855d7e4fbd67d6ee471cbf39ec6fefcc774352f7df3545835530",
    ),
    (
        "bd/catalog/funciones/v0004/catalog_option_add.sql",
        "34a392e68f6ec32801b9c622a8022b27a4a7aa766b14d81fba3e48a6c0cf8094",
    ),
    (
        "bd/catalog/funciones/v0004/catalog_option_save.sql",
        "228f76f3e56cec8ad8368d1c002b26de0958eb203e9b882c869dc904c2a67e51",
    ),
    (
        "bd/catalog/funciones/v0004/catalog_product_options_set.sql",
        "0f6bb9548bbd898d83c54af65240284af2cc4a1d552148616cdc6ae4519c0b53",
    ),
    (
        "bd/catalog/funciones/v0004/catalog_product_get.sql",
        "c741d49ebd90b7045d1e019dff80a918e530a39670dea963b4b071039e7ec510",
    ),
    (
        "bd/catalog/funciones/v0004/catalog_candidates.sql",
        "91a540c136f4e1097c65da447101a1387b070daafa66d1aeeb07fb9080af03c6",
    ),
    (
        "bd/orders/funciones/v0003/orders_recovery_request.sql",
        "ce52c7e622552c34551b2b5693a5d1d7af1735fc2b241f27affc43137b841f20",
    ),
)
NEW_FUNCTIONS = (
    "catalog_option_list",
    "catalog_option_get",
    "catalog_option_add",
    "catalog_option_save",
    "catalog_product_options_set",
    "orders_recovery_request",
)
PREVIOUS_SOURCES = (
    (
        "bd/catalog/funciones/v0003/catalog_product_get.sql",
        "45bab6a683c2376d7e110b2df69e8cc0060a6a3a3b332f12116f8ed1effd2e84",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_candidates.sql",
        "7133169658a64ad9fa1e5c6b6642df9dab1bf64dfb850a1bbc3b8aeedc5d3607",
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
)
RETIRED_FUNCTIONS = ("orders_recovery_add", "orders_recovery_list", "orders_recovery_resolve")

revision: str = "5a1c9e7d3b20"
down_revision: str | None = "c449e445ed3d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
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
    install_functions(op.get_bind(), SQL_SOURCES)
    for name in RETIRED_FUNCTIONS:
        op.execute(sa.text("DROP FUNCTION beront_api." + name + "(jsonb)"))
    op.drop_index(op.f("ix_order_recoveries_created_at"), table_name="order_recoveries")
    op.drop_index(
        op.f("uq_order_recoveries_pending"),
        table_name="order_recoveries",
        postgresql_where="(resolved_at IS NULL)",
    )
    op.drop_table("order_recoveries")


def downgrade() -> None:
    op.create_table(
        "order_recoveries",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("cedula", sa.VARCHAR(length=20), autoincrement=False, nullable=False),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False
        ),
        sa.Column(
            "resolved_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True
        ),
        sa.Column("resolved_by", sa.UUID(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["resolved_by"],
            ["administrators.id"],
            name=op.f("fk_order_recoveries_resolved_by_administrators"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_recoveries")),
    )
    op.create_index(
        op.f("uq_order_recoveries_pending"),
        "order_recoveries",
        ["cedula"],
        unique=True,
        postgresql_where="(resolved_at IS NULL)",
    )
    op.create_index(
        op.f("ix_order_recoveries_created_at"), "order_recoveries", ["created_at"], unique=False
    )
    install_functions(op.get_bind(), PREVIOUS_SOURCES)
    for name in NEW_FUNCTIONS:
        op.execute(sa.text("DROP FUNCTION beront_api." + name + "(jsonb)"))
    op.drop_index(
        op.f("ix_product_classifications_option_id"), table_name="product_classifications"
    )
    op.drop_table("product_classifications")
    op.drop_index(op.f("ix_order_recovery_attempts_ip_hash"), table_name="order_recovery_attempts")
    op.drop_index(
        op.f("ix_order_recovery_attempts_created_at"), table_name="order_recovery_attempts"
    )
    op.drop_index(op.f("ix_order_recovery_attempts_cedula"), table_name="order_recovery_attempts")
    op.drop_table("order_recovery_attempts")
    op.drop_table("classification_options")
