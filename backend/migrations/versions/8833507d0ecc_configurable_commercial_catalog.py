"""configurable_commercial_catalog"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from beront.shared.infrastructure.sql_migrations import install_functions

revision: str = "8833507d0ecc"
down_revision: str | None = "0e10c0838184"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


SQL_SOURCES = (
    (
        "bd/catalog/funciones/v0003/catalog_audience_get.sql",
        "bfdc674c6dd610336a265111dcd27266b3e9b395d6eedaa5f8a24849b26c6976",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_category_get.sql",
        "2b46065bb01f62f832ced1e510cfb512eeb0b8031781db5ff1dc0d72b9d9ebd5",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_presentation_get.sql",
        "1a89a71a1caac8ee3fcdb9dfdf77ad139b832a85f57b6bf8142e24430a35ec9c",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_audience_add.sql",
        "6f508b6d18f0f420af23e5039cd541c4120797ee5ac735b4646f95a725cf20b0",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_audience_list.sql",
        "687946ef46c58fe7bdb9c473b0271010c80ce3374203be0da405bd0b09a03bc0",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_audience_save.sql",
        "dd3bfb039fa5f6b7af0d236c214fcf0a783862d205aee2cb9962452416c79f49",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_brand_add.sql",
        "ef96ce82c6e93a3899a986e0378865c9122850f584bea3b4f6bbe91de3d33c24",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_brand_save.sql",
        "a09220c4597d42cb4c309951e0c35901af48cd580514f13b9e18075e21695bd9",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_candidates.sql",
        "7133169658a64ad9fa1e5c6b6642df9dab1bf64dfb850a1bbc3b8aeedc5d3607",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_category_add.sql",
        "f2b5776f1384d51d5dc8a28c04cb666fcf7982076dcd639fc33d7074c77b341b",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_category_list.sql",
        "ea992bae5dd395886eec178719b5c1d8e4596be36df392088798a746d9949789",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_category_save.sql",
        "b6a36bc7eca98e4280458bc5c3f8df017476f1018d3147411d38424671cecc34",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_presentation_add.sql",
        "2c6c5ff10e57b5fecbf2c06bede9dcd0cf820da69c9220fa35ddcf5076bad4fa",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_presentation_list.sql",
        "2d89186d32cec7c9b4df94aaa5cf9106ea04b8657034404fde50ff5cfa63ea9d",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_presentation_save.sql",
        "efb25966f8f58c177fe4edc72073a9bf1395c599f7b87add686abd3bc5a15446",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_product_add.sql",
        "035e16215d355d2807a08bad6cd9dfe2dd1eaba71d5abf540fef1bcf8999140c",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_product_get.sql",
        "45bab6a683c2376d7e110b2df69e8cc0060a6a3a3b332f12116f8ed1effd2e84",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_product_save.sql",
        "eae3cbfa37c689f4585508af54685d7f65e8a4978f1f2d133f62dc35583844c2",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_variant_add.sql",
        "dc148a6158f6d5e1f56bb804061c9679ed0bdb95062073c2ed8020c81d6240da",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_variant_get.sql",
        "29278a42facbd601426debd3f7cd228755ed1ae766342eac6625a233e6a046d3",
    ),
    (
        "bd/catalog/funciones/v0003/catalog_variant_save.sql",
        "ec7b6d30edbf7a7f706509190360855ac3c6e3e5bcf7afeb233fcec8879b1460",
    ),
    (
        "bd/media/funciones/v0002/media_visible.sql",
        "6dd83084eb32ba0de21db5aa794f30140664a51496dd826d00d7d92cc31f249a",
    ),
)

PREVIOUS_FUNCTIONS = (
    (
        "bd/catalog/funciones/v0001/catalog_brand_add.sql",
        "098504df0ab17ac1a3f8971861f4640ec1f4c025655193e3d2c8dc986aa11c32",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_brand_save.sql",
        "0e188e79824b893e3d03a1e18627448fd6ae51d7d238275ea3d37c3ae7d1c71c",
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
        "bd/catalog/funciones/v0002/catalog_product_get.sql",
        "39603e0d25afc98a563a4fcdaa78669236b27449b9952c76701bff4d04035318",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_product_save.sql",
        "91ab69427fed474f4757408947717436cc296ca2fa8381fda4d3c6aedb9486ef",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_variant_add.sql",
        "5852b7db442f49cda2cceb4b1a55359cc07cc35720379099b87af43780a6fa2a",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_variant_get.sql",
        "13fda3ad477eb60f21ec018142c03f8cbd7f61f53f270994713928bba4d075e4",
    ),
    (
        "bd/catalog/funciones/v0001/catalog_variant_save.sql",
        "3abf4a0b486b87cfe66e1ce1b80765157d4edcdb288bf1a632e4807ec84fe93f",
    ),
    (
        "bd/media/funciones/v0001/media_visible.sql",
        "3ab4033ae1f880db74e51588958b15dfce9d5bf9f5174bed8e1a164d73158a6b",
    ),
)


def upgrade() -> None:
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
    op.execute("""DO $guard$ BEGIN
      IF EXISTS(SELECT 1 FROM brands b LEFT JOIN products p ON p.brand_id=b.id
      LEFT JOIN LATERAL unnest(p.classifications) c(slug) ON true
      GROUP BY b.id HAVING count(DISTINCT c.slug)<>1)
      THEN RAISE EXCEPTION 'Each legacy brand needs one category before migration'; END IF;
    END $guard$""")
    op.execute("""INSERT INTO categories(id,slug,name_es,name_en,active,version)
      SELECT md5('category:'||slug)::uuid,slug,slug,slug,true,1
      FROM (SELECT DISTINCT unnest(classifications) slug FROM products) s""")
    op.execute("""INSERT INTO audiences(id,slug,name_es,name_en,active,version)
      SELECT md5('audience:'||audience)::uuid,audience,audience,audience,true,1 FROM products GROUP BY audience""")
    op.execute("""INSERT INTO presentations(id,name_es,name_en,kind,volume_ml,active,version)
      SELECT md5('presentation:'||kind||':'||volume_ml)::uuid,volume_ml||' ml',volume_ml||' ml',kind,volume_ml,true,1
      FROM variants GROUP BY kind,volume_ml""")
    op.add_column("brands", sa.Column("category_id", sa.Uuid(), nullable=True))
    op.execute("""UPDATE brands b SET category_id=(SELECT c.id FROM products p
      CROSS JOIN LATERAL unnest(p.classifications) s(slug) JOIN categories c ON c.slug=s.slug
      WHERE p.brand_id=b.id LIMIT 1)""")
    op.alter_column("brands", "category_id", nullable=False)
    op.drop_constraint(op.f("ck_products_audience"), "products", type_="check")
    op.create_index(op.f("ix_brands_category_id"), "brands", ["category_id"], unique=False)
    op.create_foreign_key(
        op.f("fk_brands_category_id_categories"), "brands", "categories", ["category_id"], ["id"]
    )
    op.alter_column(
        "products",
        "audience",
        existing_type=sa.VARCHAR(length=10),
        type_=sa.String(length=64),
        existing_nullable=False,
    )
    op.drop_index(
        op.f("ix_products_classifications"), table_name="products", postgresql_using="gin"
    )
    op.create_index(op.f("ix_products_audience"), "products", ["audience"], unique=False)
    op.create_foreign_key(
        op.f("fk_products_audience_audiences"), "products", "audiences", ["audience"], ["slug"]
    )
    op.drop_column("products", "classifications")
    op.create_foreign_key(
        "fk_variants_presentation",
        "variants",
        "presentations",
        ["kind", "volume_ml"],
        ["kind", "volume_ml"],
    )
    install_functions(op.get_bind(), SQL_SOURCES)


def downgrade() -> None:
    op.drop_constraint("fk_variants_presentation", "variants", type_="foreignkey")
    op.execute("""DO $guard$ BEGIN
      IF EXISTS(SELECT 1 FROM categories WHERE slug NOT IN ('arabic','designer','niche'))
      OR EXISTS(SELECT 1 FROM products WHERE audience NOT IN ('male','female','unisex'))
      THEN RAISE EXCEPTION 'Previous schema cannot represent configured categories or audiences'; END IF;
    END $guard$""")
    op.add_column(
        "products",
        sa.Column("classifications", postgresql.ARRAY(sa.VARCHAR(length=12)), nullable=True),
    )
    op.execute("""UPDATE products p SET classifications=ARRAY[c.slug]::varchar[]
      FROM brands b JOIN categories c ON c.id=b.category_id WHERE b.id=p.brand_id""")
    op.alter_column("products", "classifications", nullable=False)
    op.create_check_constraint(
        op.f("ck_products_classifications"),
        "products",
        "classifications <@ ARRAY['arabic','designer','niche']::varchar[]",
    )
    op.create_check_constraint(
        op.f("ck_products_audience"), "products", "audience IN ('male','female','unisex')"
    )
    op.drop_constraint(op.f("fk_products_audience_audiences"), "products", type_="foreignkey")
    op.drop_index(op.f("ix_products_audience"), table_name="products")
    op.create_index(
        op.f("ix_products_classifications"),
        "products",
        ["classifications"],
        unique=False,
        postgresql_using="gin",
    )
    op.alter_column(
        "products",
        "audience",
        existing_type=sa.String(length=64),
        type_=sa.VARCHAR(length=10),
        existing_nullable=False,
    )
    op.drop_constraint(op.f("fk_brands_category_id_categories"), "brands", type_="foreignkey")
    op.drop_index(op.f("ix_brands_category_id"), table_name="brands")
    op.drop_column("brands", "category_id")
    op.drop_table("presentations")
    op.drop_table("categories")
    op.drop_table("audiences")
    install_functions(op.get_bind(), PREVIOUS_FUNCTIONS)
    old_names = {relative.rsplit("/", 1)[1] for relative, _ in PREVIOUS_FUNCTIONS}
    for relative, _ in SQL_SOURCES:
        if relative.rsplit("/", 1)[1] not in old_names:
            name = relative.rsplit("/", 1)[1].removesuffix(".sql")
            op.execute(sa.text("DROP FUNCTION beront_api." + name + "(jsonb)"))
