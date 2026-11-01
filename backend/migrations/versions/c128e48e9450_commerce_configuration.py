"""commerce_configuration"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from beront.shared.infrastructure.sql_migrations import install_functions

revision: str = "c128e48e9450"
down_revision: str | None = "8833507d0ecc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


SQL_SOURCES = (
    (
        "bd/commerce/funciones/v0001/commerce_bank_add.sql",
        "335e4bfc1ab78991f8b80bf1ff1bbf3bb68d39463f7470c0d0fd35037c4fba0d",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_bank_get.sql",
        "7ce9c70191975c635712a841c173aa93d6ba72ce040e8f5ec12317aac90a597b",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_bank_list.sql",
        "80407d82d8c16bebeeeecc547890e7382ce444434a337e4c2342cf3253206273",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_bank_save.sql",
        "7d9dfdf42abf2b3e41895725c81342a86bdb781ce36087bdacd7a937b06c582f",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_city_add.sql",
        "8343014e53b13ccb549cd7fe9c8b30050fdeccf131c418d106b334564cfc7555",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_city_get.sql",
        "58f2f95e4effa76a90d2b63e8233e126fdcd1c335492ea6af12fb06ec62e8394",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_city_list.sql",
        "353c4c114d44370c78ae327e423a6c556c22b9e698d1043a8eb192949527cc93",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_city_save.sql",
        "fbed1ba60d8dc1b80d5bd35377061b017456e350dc39394a6fa089055fb6273d",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_destination.sql",
        "1733c187849a24ad7a09718d59e44a309d246248e00f9dc14050834d4894985c",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_province_add.sql",
        "1c26b1f24c4d76257c601624e7d66b4e3d171fa1a2640fc4aedfc77b03cf83ad",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_province_get.sql",
        "66ed91eae0f9f14b603e0097affc72a480abec1254dea93588665f08764897c2",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_province_list.sql",
        "515fb3423214d95831e6bb57c20071c691d3dd8e0d4f3317c0fa2b68f7bdd1bf",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_province_save.sql",
        "d940ad648814a6b933d1ea5dd347f75bbac277901e212c3511998e35476893f3",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_settings_get.sql",
        "ecaaf51d8eafe93c58ec4c76248aa18e5fdddbbb25e72143c3a8beda834e59cf",
    ),
    (
        "bd/commerce/funciones/v0001/commerce_settings_save.sql",
        "0aa1eac12f4aea7814e16266ed60f3e7f3d161d878262ce3526023581d041b7c",
    ),
)


def upgrade() -> None:
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
    install_functions(op.get_bind(), SQL_SOURCES)


def downgrade() -> None:
    for relative, _ in reversed(SQL_SOURCES):
        name = relative.rsplit("/", 1)[1].removesuffix(".sql")
        op.execute(sa.text("DROP FUNCTION beront_api." + name + "(jsonb)"))
    op.drop_index(op.f("ix_cities_province_id"), table_name="cities")
    op.drop_table("cities")
    op.drop_table("store_settings")
    op.drop_table("provinces")
    op.drop_table("bank_accounts")
