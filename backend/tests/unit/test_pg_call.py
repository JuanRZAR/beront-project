from decimal import Decimal
from uuid import uuid4

import pytest

from beront.shared.infrastructure.pg_call import PgCall, encode_payload


def test_pg_call_rejects_unregistered_functions_before_accessing_database():
    class Connection:
        def execute(self, *args):
            raise AssertionError("Database must not be called")

    pg = PgCall(Connection())
    for name in ("DROP TABLE products", "catalog_product_get;SELECT 1", "pg_read_file", "unknown"):
        with pytest.raises(ValueError):
            pg.call(name, {})


def test_pg_call_binds_values_instead_of_interpolating_sql():
    calls = []

    class Connection:
        def execute(self, query, parameters):
            calls.append((query.as_string(), parameters))
            return self

        def fetchone(self):
            return {"result": {"ok": True}}

    attack = "'; DROP TABLE products; --"
    assert PgCall(Connection()).call("identity_admin_get", {"username": attack}) == {"ok": True}
    query, parameters = calls[0]
    assert attack not in query
    assert parameters[0].obj == {"username": attack}
    assert '"beront_api"."identity_admin_get"(%s)' in query


def test_pg_payload_preserves_money_and_identifiers():
    import json

    identifier = uuid4()
    payload = json.loads(encode_payload({"id": identifier, "price": Decimal("9999999999.99")}))
    assert payload == {"id": str(identifier), "price": "9999999999.99"}
    with pytest.raises(TypeError):
        encode_payload({"unsupported": object()})
