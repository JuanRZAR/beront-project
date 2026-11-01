import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

from beront.shared.infrastructure.database import Base


def test_migrations_match_models_and_runtime_has_no_ddl(database):
    _, runtime, engine = database
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        assert compare_metadata(context, Base.metadata) == []
    runtime_engine = create_engine(runtime)
    try:
        with runtime_engine.connect() as connection:
            assert (
                connection.scalar(
                    text("SELECT has_schema_privilege(current_user, 'public', 'CREATE')")
                )
                is False
            )
            with pytest.raises(ProgrammingError):
                connection.execute(text("SELECT * FROM alembic_version"))
        with runtime_engine.connect() as connection:
            with pytest.raises(ProgrammingError):
                connection.execute(text("SELECT * FROM products"))
    finally:
        runtime_engine.dispose()
