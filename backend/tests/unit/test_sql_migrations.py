import re

import pytest

from beront.shared.infrastructure.sql_migrations import (
    BACKEND,
    FUNCTIONS_ROOT,
    function_sources,
    install_functions,
)


def test_installer_rejects_sources_outside_function_root_before_executing_sql():
    class Connection:
        def execution_options(self, **kwargs):
            raise AssertionError("SQL must not execute")

    with pytest.raises(ValueError, match="outside"):
        install_functions(Connection(), ["bd/identity/funciones/identity_admin_get.sql", ".env"])
    with pytest.raises(ValueError, match="outside"):
        install_functions(Connection(), ["bd/../.env"])
    with pytest.raises(ValueError, match="outside"):
        install_functions(Connection(), ["bd/identity/README.md"])


def test_function_sources_are_flat_and_named_after_their_function():
    sources = function_sources()
    assert sources
    assert len(sources) == len({path.rsplit("/", 1)[1] for path in sources})
    assert not [p for p in FUNCTIONS_ROOT.rglob("*") if re.fullmatch(r"v\d+", p.name)]
    for relative in sources:
        path = BACKEND / relative
        defined = re.findall(
            r"CREATE OR REPLACE FUNCTION beront_api\.(\w+)\(", path.read_text(encoding="utf-8")
        )
        assert defined == [path.stem], relative
