from pathlib import Path

from sqlalchemy import text

BACKEND = Path(__file__).resolve().parents[4]
FUNCTIONS_ROOT = (BACKEND / "bd").resolve()


def function_sources():
    return sorted(
        path.relative_to(BACKEND).as_posix() for path in FUNCTIONS_ROOT.glob("*/funciones/*.sql")
    )


def install_functions(connection, sources):
    paths = [(BACKEND / relative).resolve() for relative in sources]
    if any(not path.is_relative_to(FUNCTIONS_ROOT) or path.suffix != ".sql" for path in paths):
        raise ValueError("SQL migration source is outside backend/bd/")
    # Las funciones se llaman entre sí; sin esto el orden de instalación importaría.
    run(connection, "SET LOCAL check_function_bodies = off")
    for path in paths:
        run(connection, path.read_text(encoding="utf-8"))


def run(connection, statement):
    if hasattr(connection, "exec_driver_sql"):
        connection.execution_options(no_parameters=True).exec_driver_sql(statement)
    else:
        connection.execute(text(statement))
