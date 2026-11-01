"""Single owner and versioned PostgreSQL functions."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from beront.shared.infrastructure.sql_migrations import install_functions

revision: str = "331982957841"
down_revision: str | None = "e58826a8b8c7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SQL_SOURCES = (
    (
        "bd/comunes/funciones/v0001/audit_record.sql",
        "abe117e6ff476c2069a80d4a82bb8570c91f6282353213a9133f8b09a24bd7cf",
    ),
    (
        "bd/identity/funciones/v0001/identity_admin_get.sql",
        "f34bf8406e9e6488caae8470067f36fd8fab1e854e8abde18ff237f493d1504c",
    ),
    (
        "bd/identity/funciones/v0001/identity_admin_create.sql",
        "3831f3203b02b21db7f0d41d90c69b11cd7a99f4158e8a36901a652b4b5e3237",
    ),
    (
        "bd/identity/funciones/v0001/identity_password_set.sql",
        "c6f0d50287e66059cf09d70aa9da1bb9b2efd19f704dfd03a118c9d45eaa000f",
    ),
    (
        "bd/identity/funciones/v0001/identity_session_get.sql",
        "f7d1ce221b8a26a2111328a5eab25fcb701384a02ce9f8e03bef79e0b32fa482",
    ),
    (
        "bd/identity/funciones/v0001/identity_session_add.sql",
        "75f1896d751170e6dd3e626f8702c6afbfdfd534449511635af4e64edffaaa7e",
    ),
    (
        "bd/identity/funciones/v0001/identity_session_touch.sql",
        "103cfd209dd3356d1b36d1de1c9fe164cdc4be34007db6beaa4aed9f263eb039",
    ),
    (
        "bd/identity/funciones/v0001/identity_session_revoke.sql",
        "413b3d0c41dfa4ec103909ad9ddcfd8541037133d7e8e60b91a7cc622ab726d7",
    ),
    (
        "bd/identity/funciones/v0001/identity_sessions_revoke_all.sql",
        "960dd1ea61006cb6ca551f0727294d637ee181d73c25f218dcae0d18d2f269fd",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_product_get.sql",
        "e00ae1790909ec89384547abf316790f2547655560fedd4bb5678efda75fe445",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_product_by_slug.sql",
        "58adaac48749eed7ecc1fb686eb0831494e2b19458836d9d56815dcc1ab89aa4",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_candidates.sql",
        "50932d1c32a540e240c287b6c56853ffb52e6a48ccc2583683b68942da83ab42",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_product_add.sql",
        "d480c673ce23977a91d0173b5ad00edae00da171f5d8df49e0d936c249f49798",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_product_save.sql",
        "91ab69427fed474f4757408947717436cc296ca2fa8381fda4d3c6aedb9486ef",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_variant_get.sql",
        "13fda3ad477eb60f21ec018142c03f8cbd7f61f53f270994713928bba4d075e4",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_variant_add.sql",
        "5852b7db442f49cda2cceb4b1a55359cc07cc35720379099b87af43780a6fa2a",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_variant_save.sql",
        "3abf4a0b486b87cfe66e1ce1b80765157d4edcdb288bf1a632e4807ec84fe93f",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_brands.sql",
        "b8208be53530c3eadfc379d902908e4f8517e5b589a86f826421a944193a9c4c",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_brand_get.sql",
        "4fe3f28fd0b87d62776e0bdd3eb837365deefcccf60c89a1cb188dab7cc0790e",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_brand_add.sql",
        "098504df0ab17ac1a3f8971861f4640ec1f4c025655193e3d2c8dc986aa11c32",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_brand_save.sql",
        "0e188e79824b893e3d03a1e18627448fd6ae51d7d238275ea3d37c3ae7d1c71c",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_image_get.sql",
        "0343d3f0cf34eecf4abe42dc0501c84ca0d9e384cf2084f543a956eeea070a00",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_image_by_filename.sql",
        "35158358e21b7c6bf726eba33c9b8c75464b0a5fe167f23c06c529859395c604",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_image_add.sql",
        "f7e3d1163a10e2db888fbafaf5d742d3952f5fcc417267def5c7f2be5f313e80",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_image_save.sql",
        "209510930a8eeea67baf8ff275949ce3d76a4bad9c2869f516f6680a3618d577",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_image_delete.sql",
        "66ebfd7c1a64978cd7e09e01878ddd7a5e029b50a9d1c66b9a760719430ff038",
    ),
    (
        "bd/inventory/funciones/v0001/inventory_ensure_decants.sql",
        "f9c96c9e1320eb5e7ef6acfd075f6a5c0fc0a3e39218f994c2bb956a9b438f02",
    ),
    (
        "bd/inventory/funciones/v0001/inventory_ensure_bottles.sql",
        "e72583294874e95e834d44aeba832ed6d082e9f82be52ed4bed5c0fb6b2ba3be",
    ),
    (
        "bd/inventory/funciones/v0001/inventory_amounts.sql",
        "8f91a1b900a5260d3b2314b09e69ee318f7a44940a3688a7b7af2099bdca32fa",
    ),
    (
        "bd/inventory/funciones/v0001/inventory_balance_get.sql",
        "77a4027354002fd20808b9d2d5f797717d22851cf4e0c07a7154d91ab20fd301",
    ),
    (
        "bd/inventory/funciones/v0001/inventory_balance_save.sql",
        "683ea7bf2deed3d27d5355bc350d659d6fd50117ca370e701fcd5dd4417abc57",
    ),
    (
        "bd/inventory/funciones/v0001/inventory_movement_get.sql",
        "b1102a848ea283b22f8c58389df5dfc03ca03d49ce474f6c08e977abce102b1b",
    ),
    (
        "bd/inventory/funciones/v0001/inventory_movement_add.sql",
        "ff40aeed5060cd96142f61f85c16e2f9c44b2179f03ed153d1cec3c56207d8d3",
    ),
    (
        "bd/inventory/funciones/v0001/inventory_balances.sql",
        "5aca744940fad184068664249b9f837f13a96100e55fb34915e1a6e6309caf8d",
    ),
    (
        "bd/inventory/funciones/v0001/inventory_movements.sql",
        "30f4f720919aeaeb3715473b340e33cf35f78bb6a136be0a08187d9cdd1dbaa6",
    ),
)


def upgrade() -> None:
    op.add_column("administrators", sa.Column("singleton_slot", sa.Integer(), nullable=True))
    op.execute("UPDATE administrators SET singleton_slot = 1")
    op.alter_column("administrators", "singleton_slot", nullable=False)
    op.create_unique_constraint(
        "uq_administrators_singleton_slot", "administrators", ["singleton_slot"]
    )
    op.create_check_constraint(
        "ck_administrators_single_administrator", "administrators", "singleton_slot = 1"
    )
    op.execute("CREATE SCHEMA beront_api")
    op.execute("REVOKE ALL ON SCHEMA beront_api FROM PUBLIC")
    install_functions(op.get_bind(), SQL_SOURCES)


def downgrade() -> None:
    for relative, _ in reversed(SQL_SOURCES):
        name = relative.rsplit("/", 1)[1].removesuffix(".sql")
        op.execute(sa.text("DROP FUNCTION beront_api." + name + "(jsonb)"))
    op.execute("DROP SCHEMA beront_api")
    op.drop_constraint("ck_administrators_single_administrator", "administrators", type_="check")
    op.drop_constraint("uq_administrators_singleton_slot", "administrators", type_="unique")
    op.drop_column("administrators", "singleton_slot")
