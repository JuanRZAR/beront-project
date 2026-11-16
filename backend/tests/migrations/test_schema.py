from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from beront.shared.infrastructure.database import Base


def test_migrations_match_models(database):
    with database[2].connect() as connection:
        context = MigrationContext.configure(connection)
        assert compare_metadata(context, Base.metadata) == []
