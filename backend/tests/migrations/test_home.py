from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from conftest import alembic_config
from sqlalchemy import inspect

from beront.shared.infrastructure.modelos import Base


def test_home_migration_round_trip(database):
    engine = database[2]
    with engine.begin() as connection:
        config = alembic_config(connection)
        command.downgrade(config, "49ce23c2f0c8")
        assert "featured_messages" not in inspect(connection).get_table_names()
        command.upgrade(config, "head")
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
