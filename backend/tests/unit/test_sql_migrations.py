import pytest

from beront.shared.infrastructure.sql_migrations import install_functions


def test_migrations_reject_changed_hashes_before_executing_sql():
    class Connection:
        def execution_options(self, **kwargs):
            raise AssertionError("SQL must not execute")

    with pytest.raises(ValueError, match="immutable"):
        install_functions(
            Connection(), [("bd/identity/funciones/v0001/identity_admin_get.sql", "0" * 64)]
        )
    with pytest.raises(ValueError, match="outside"):
        install_functions(Connection(), [("backend/.env", "0" * 64)])
