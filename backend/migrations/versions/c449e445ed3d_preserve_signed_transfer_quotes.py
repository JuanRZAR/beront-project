"""Preserve server-signed quotes for transfers already sent."""

from alembic import op

from beront.shared.infrastructure.sql_migrations import install_functions

revision = "c449e445ed3d"
down_revision = "d8893d51a976"
branch_labels = None
depends_on = None
SQL_SOURCES = (
    (
        "bd/orders/funciones/v0002/orders_add.sql",
        "9f457fe2f3230923c48ae31a372640e5e8930a0d5132c5205bca723d9f5c29b9",
    ),
)
PREVIOUS_FUNCTIONS = (
    (
        "bd/orders/funciones/v0001/orders_add.sql",
        "19053e249bf8af59340d26e3466876b0e6866d38db1fa9727389f4301ac08c59",
    ),
)


def upgrade():
    install_functions(op.get_bind(), SQL_SOURCES)


def downgrade():
    install_functions(op.get_bind(), PREVIOUS_FUNCTIONS)
