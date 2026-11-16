from decimal import Decimal

from psycopg.pq import Format

from beront.shared.infrastructure.database import PgDatabase

JSONB = 3802


def test_connections_reuse_one_json_loader(database):
    db = PgDatabase(database[1])
    loaders = set()
    for _ in range(3):
        with db.connect() as connection:
            loaders.add(connection.adapters.get_loader(JSONB, Format.TEXT))
            assert connection.execute("SELECT '{\"x\": 1.10}'::jsonb AS value").fetchone()[
                "value"
            ] == {"x": Decimal("1.10")}
    assert len(loaders) == 1
