"""pinned function search path"""

from collections.abc import Sequence

from alembic import op

from beront.shared.infrastructure.sql_migrations import function_sources, install_functions

revision: str = "699c6eca196d"
down_revision: str | None = "de252c02c932"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    install_functions(op.get_bind(), function_sources())


def downgrade() -> None:
    # The pg_temp suffix stays: it only narrows name resolution.
    pass
