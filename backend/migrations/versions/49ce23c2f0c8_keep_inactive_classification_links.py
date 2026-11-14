"""keep inactive classification links

Revision ID: 49ce23c2f0c8
Revises: 87313231bdf2
"""

from collections.abc import Sequence

from alembic import op

from beront.shared.infrastructure.sql_migrations import install_functions

revision: str = "49ce23c2f0c8"
down_revision: str | None = "87313231bdf2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SOURCES = ["bd/catalog/funciones/catalog_product_options_set.sql"]


def upgrade() -> None:
    install_functions(op.get_bind(), SOURCES)


def downgrade() -> None:
    # La definición anterior se recupera desde Git.
    pass
