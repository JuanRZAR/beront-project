import hashlib
from pathlib import Path

from sqlalchemy import text

PROJECT = Path(__file__).resolve().parents[5]


def install_functions(connection, sources):
    allowed_root = (PROJECT / "bd").resolve()
    for relative, expected_hash in sources:
        path = (PROJECT / relative).resolve()
        if not path.is_relative_to(allowed_root) or path.suffix != ".sql":
            raise ValueError("SQL migration source is outside bd/")
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != expected_hash:
            raise ValueError("An immutable SQL migration source has changed: " + relative)
        body = content.decode("utf-8")
        if hasattr(connection, "exec_driver_sql"):
            connection.execution_options(no_parameters=True).exec_driver_sql(body)
        else:
            connection.execute(text(body))
