"""reusable_media_library"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from beront.shared.infrastructure.sql_migrations import install_functions

revision: str = "0e10c0838184"
down_revision: str | None = "331982957841"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


SQL_SOURCES = (
    (
        "bd/media/funciones/v0001/media_get.sql",
        "8aa42cfaa121c1163e8130415ff66fd8868c4a5a28ea97c02ee44bc7880e85da",
    ),
    (
        "bd/media/funciones/v0001/media_register.sql",
        "a53b5084eee16887f749f64fc1e15b7a2b6e693bf451e33d6a20f8c4999a18b5",
    ),
    (
        "bd/media/funciones/v0001/media_list.sql",
        "8daa09e0cbfef4925df6ecf4b559ab8aa7e7b0f031e03c15407218abb89f9129",
    ),
    (
        "bd/media/funciones/v0001/media_update.sql",
        "9e0a064e2ce623358d852e6b3c1f908bc3688cbd1b4d2553a3976eeb00471dfc",
    ),
    (
        "bd/media/funciones/v0001/media_delete.sql",
        "db7d21b71efa0e7533a0a2396c863fe676c86ed847ae9d84edcfbf0d5ef3e75c",
    ),
    (
        "bd/media/funciones/v0001/media_visible.sql",
        "3ab4033ae1f880db74e51588958b15dfce9d5bf9f5174bed8e1a164d73158a6b",
    ),
    (
        "bd/catalog/funciones/v0002/catalog_product_get.sql",
        "39603e0d25afc98a563a4fcdaa78669236b27449b9952c76701bff4d04035318",
    ),
    (
        "bd/catalog/funciones/v0002/catalog_image_get.sql",
        "5d6b198dbddb8b51aeec54e9370f1e2ed0703cff3babcfda1142ff10eb63cd18",
    ),
    (
        "bd/catalog/funciones/v0002/catalog_image_by_filename.sql",
        "2ff70511d62c6af7a1dbdbfb2920ea92dfbf5a66be42d370964e35e45bd377cf",
    ),
    (
        "bd/catalog/funciones/v0002/catalog_image_add.sql",
        "5b0e46c88d627d974425b3f320ab3547b8831518601e2268235df318993a373f",
    ),
)
PREVIOUS_FUNCTIONS = (
    (
        "bd/catalog/funciones/v0001/catalog_product_get.sql",
        "e00ae1790909ec89384547abf316790f2547655560fedd4bb5678efda75fe445",
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
)


def upgrade() -> None:
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
    op.execute(
        "INSERT INTO media_assets(id,filename,url,name,kind,created_at,version) SELECT id,filename,'/media/'||filename,alt_es,'product',CURRENT_TIMESTAMP,1 FROM product_images"
    )
    op.add_column("product_images", sa.Column("asset_id", sa.Uuid(), nullable=True))
    op.execute("UPDATE product_images SET asset_id=id")
    op.alter_column("product_images", "asset_id", nullable=False)
    op.drop_constraint(op.f("uq_product_images_filename"), "product_images", type_="unique")
    op.create_index(
        op.f("ix_product_images_asset_id"), "product_images", ["asset_id"], unique=False
    )
    op.create_unique_constraint(
        "uq_product_images_product_asset", "product_images", ["product_id", "asset_id"]
    )
    op.create_foreign_key(
        op.f("fk_product_images_asset_id_media_assets"),
        "product_images",
        "media_assets",
        ["asset_id"],
        ["id"],
    )
    op.drop_column("product_images", "filename")
    install_functions(op.get_bind(), SQL_SOURCES)


def downgrade() -> None:
    if op.get_bind().scalar(
        sa.text("SELECT EXISTS(SELECT 1 FROM product_images GROUP BY asset_id HAVING count(*)>1)")
    ):
        raise RuntimeError("The previous schema cannot represent shared media assets")
    for relative, _ in reversed(SQL_SOURCES):
        if "/media/" in relative:
            name = relative.rsplit("/", 1)[1].removesuffix(".sql")
            op.execute(sa.text("DROP FUNCTION beront_api." + name + "(jsonb)"))
    op.add_column("product_images", sa.Column("filename", sa.VARCHAR(length=50), nullable=True))
    op.execute(
        "UPDATE product_images i SET filename=a.filename FROM media_assets a WHERE a.id=i.asset_id"
    )
    op.alter_column("product_images", "filename", nullable=False)
    op.drop_constraint(
        op.f("fk_product_images_asset_id_media_assets"), "product_images", type_="foreignkey"
    )
    op.drop_constraint("uq_product_images_product_asset", "product_images", type_="unique")
    op.drop_index(op.f("ix_product_images_asset_id"), table_name="product_images")
    op.create_unique_constraint(
        op.f("uq_product_images_filename"),
        "product_images",
        ["filename"],
        postgresql_nulls_not_distinct=False,
    )
    op.drop_column("product_images", "asset_id")
    install_functions(op.get_bind(), PREVIOUS_FUNCTIONS)
    op.drop_index(op.f("ix_media_assets_created_at"), table_name="media_assets")
    op.drop_table("media_assets")
