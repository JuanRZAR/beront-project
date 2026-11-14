"""featured home messages"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from beront.shared.infrastructure.sql_migrations import install_functions

revision: str = "de252c02c932"
down_revision: str | None = "49ce23c2f0c8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "featured_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("primary_path", sa.String(length=250), nullable=False),
        sa.Column("secondary_path", sa.String(length=250), nullable=False),
        sa.Column("icon", sa.String(length=20), nullable=False),
        sa.Column("stats_kind", sa.String(length=20), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "icon IN ('bottle','truck','whatsapp','tag')",
            name=op.f("ck_featured_messages_message_icon"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(content) = 'object' AND content ?& ARRAY['es','en']",
            name=op.f("ck_featured_messages_message_languages"),
        ),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name=op.f("ck_featured_messages_message_slug")
        ),
        sa.CheckConstraint(
            "stats_kind IN ('none','decant','full_bottle')",
            name=op.f("ck_featured_messages_message_stats"),
        ),
        sa.CheckConstraint(
            "position BETWEEN 0 AND 1000 AND version > 0",
            name=op.f("ck_featured_messages_message_order"),
        ),
        sa.CheckConstraint(
            "starts_at IS NULL OR ends_at IS NULL OR starts_at < ends_at",
            name=op.f("ck_featured_messages_message_dates"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_featured_messages")),
        sa.UniqueConstraint("slug", name=op.f("uq_featured_messages_slug")),
    )
    op.create_table(
        "featured_message_images",
        sa.Column("message_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint(
            "position BETWEEN 0 AND 2", name=op.f("ck_featured_message_images_message_image_order")
        ),
        sa.ForeignKeyConstraint(
            ["asset_id"],
            ["media_assets.id"],
            name=op.f("fk_featured_message_images_asset_id_media_assets"),
        ),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["featured_messages.id"],
            name=op.f("fk_featured_message_images_message_id_featured_messages"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("message_id", "position", name=op.f("pk_featured_message_images")),
        sa.UniqueConstraint("message_id", "asset_id", name="uq_featured_message_images_asset"),
    )
    op.create_index(
        op.f("ix_featured_message_images_asset_id"),
        "featured_message_images",
        ["asset_id"],
        unique=False,
    )
    install_functions(
        op.get_bind(),
        [
            "bd/commerce/funciones/commerce_message_get.sql",
            "bd/commerce/funciones/commerce_message_list.sql",
            "bd/commerce/funciones/commerce_message_add.sql",
            "bd/commerce/funciones/commerce_message_save.sql",
            "bd/media/funciones/media_visible.sql",
            "bd/media/funciones/media_delete.sql",
        ],
    )


def downgrade() -> None:
    for name in (
        "commerce_message_list",
        "commerce_message_add",
        "commerce_message_save",
        "commerce_message_get",
    ):
        op.execute(f"DROP FUNCTION beront_api.{name}(jsonb)")
    op.execute("""
CREATE OR REPLACE FUNCTION beront_api.media_visible(p jsonb) RETURNS jsonb
LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, public, beront_api AS $function$
SELECT to_jsonb(a) FROM public.media_assets a WHERE a.filename=p->>'filename'
 AND (COALESCE((p->>'private')::boolean,false) OR (a.kind='product' AND EXISTS(
 SELECT 1 FROM public.product_images i JOIN public.products pr ON pr.id=i.product_id JOIN public.brands b ON b.id=pr.brand_id JOIN public.categories c ON c.id=b.category_id JOIN public.audiences au ON au.slug=pr.audience
 WHERE i.asset_id=a.id AND pr.published AND NOT pr.archived AND b.active AND c.active AND au.active)));
$function$;
""")
    op.execute("""
CREATE OR REPLACE FUNCTION beront_api.media_delete(p jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public, beront_api AS $function$
DECLARE asset public.media_assets%ROWTYPE;
BEGIN
 SELECT * INTO asset FROM public.media_assets WHERE id=(p->>'id')::uuid AND kind='product' FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION USING MESSAGE='NOT_FOUND'; END IF;
 IF asset.version<>(p->>'version')::integer THEN RAISE EXCEPTION USING MESSAGE='VERSION_CONFLICT'; END IF;
 IF EXISTS(SELECT 1 FROM public.product_images WHERE asset_id=asset.id) THEN RAISE EXCEPTION USING MESSAGE='ASSET_IN_USE'; END IF;
 DELETE FROM public.media_assets WHERE id=asset.id;
 RETURN to_jsonb(asset);
END;
$function$;
""")
    op.drop_index(op.f("ix_featured_message_images_asset_id"), table_name="featured_message_images")
    op.drop_table("featured_message_images")
    op.drop_table("featured_messages")
