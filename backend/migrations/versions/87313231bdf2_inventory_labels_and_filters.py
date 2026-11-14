"""inventory labels and filters

Revision ID: 87313231bdf2
Revises: 0e7393567f81
"""

from collections.abc import Sequence

from alembic import op

from beront.shared.infrastructure.sql_migrations import install_functions

revision: str = "87313231bdf2"
down_revision: str | None = "0e7393567f81"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SOURCES = [
    "bd/inventory/funciones/inventory_balances.sql",
    "bd/inventory/funciones/inventory_movements.sql",
]


def upgrade() -> None:
    install_functions(op.get_bind(), SOURCES)


def downgrade() -> None:
    # La definición anterior se recupera desde Git; los campos añadidos son compatibles.
    pass
