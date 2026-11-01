import json
from decimal import Decimal
from functools import partial

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import set_json_loads

from beront.shared.infrastructure.modelos.base import Base as Base
from beront.shared.infrastructure.modelos.base import now as now
from beront.shared.infrastructure.modelos.comunes.tables import AuditEventModel as AuditEventModel
from beront.shared.infrastructure.pg_call import PgCall


class PgDatabase:
    def __init__(self, url):
        self.dsn = url.replace("postgresql+psycopg://", "postgresql://", 1)

    def connect(self):
        connection = psycopg.connect(
            self.dsn,
            connect_timeout=5,
            options="-c statement_timeout=10000 -c timezone=UTC",
            row_factory=dict_row,
        )
        set_json_loads(partial(json.loads, parse_float=Decimal), connection)
        return connection

    def dispose(self):
        pass


def make_database(url):
    database = PgDatabase(url)
    return database, database.connect


class SqlUnitOfWork:
    def __init__(self, connection_factory, repositories):
        self.connection_factory = connection_factory
        self.repositories = repositories

    def __enter__(self):
        self.connection = self.connection_factory()
        self.pg = PgCall(self.connection)
        for name, factory in self.repositories.items():
            setattr(self, name, factory(self.pg))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.connection.rollback()
        finally:
            self.connection.close()

    def commit(self):
        self.connection.commit()

    def audit(self, actor_id, action, resource_id=None, request_id=None):
        self.pg.call(
            "audit_record",
            {
                "actor_id": actor_id,
                "action": action,
                "resource_id": str(resource_id) if resource_id is not None else None,
                "request_id": request_id,
            },
        )
