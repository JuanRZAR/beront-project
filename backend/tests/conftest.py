import contextlib
import os
import secrets
import shutil
import socket
import subprocess
import tempfile
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from psycopg import sql
from sqlalchemy import create_engine

from beront.app import create_app
from beront.config import Settings

BACKEND = Path(__file__).resolve().parents[1]
PASSWORD = "Temporary test password 12345"


def alembic_config(connection=None):
    config = Config(str(BACKEND / "alembic.ini"))
    if connection is not None:
        config.attributes["connection"] = connection
    return config


@contextlib.contextmanager
def isolated_postgres(root):
    bin_path = Path(os.environ.get("POSTGRES_BIN", r"C:\Program Files\PostgreSQL\18\bin"))
    suffix = ".exe" if os.name == "nt" else ""
    initdb = bin_path / ("initdb" + suffix)
    if not initdb.exists():
        found = shutil.which("initdb")
        if not found:
            raise RuntimeError("Configura POSTGRES_BIN para ejecutar pruebas con PostgreSQL real.")
        bin_path = Path(found).parent
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    password = secrets.token_urlsafe(32)
    password_file = root / "pg-password"
    password_file.write_text(password, encoding="utf-8")
    data = root / "data"
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

    def run(arguments):
        stdout_path, stderr_path = root / "command.stdout", root / "command.stderr"
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            result = subprocess.run(
                arguments,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                creationflags=flags,
                timeout=60,
            )
        if result.returncode:
            raise RuntimeError(
                "PostgreSQL de pruebas: "
                + stderr_path.read_text(encoding="utf-8", errors="replace")[-2000:]
            )
        return result

    run(
        [
            str(bin_path / ("initdb" + suffix)),
            "-D",
            str(data),
            "-U",
            "beront_migrator",
            "--auth=scram-sha-256",
            "--pwfile=" + str(password_file),
            "--encoding=UTF8",
            "--locale=C",
        ]
    )
    password_file.unlink()
    control = str(bin_path / ("pg_ctl" + suffix))
    run(
        [
            control,
            "-D",
            str(data),
            "-l",
            str(root / "postgres.log"),
            "-o",
            f"-h 127.0.0.1 -p {port} -F",
            "-w",
            "start",
        ]
    )
    connection = {
        "host": "127.0.0.1",
        "port": port,
        "user": "beront_migrator",
        "password": password,
        "dbname": "postgres",
    }
    try:
        with psycopg.connect(**connection, autocommit=True) as db:
            db.execute(
                sql.SQL("CREATE ROLE beront_app LOGIN PASSWORD {}").format(sql.Literal(password))
            )
        yield connection
    finally:
        run([control, "-D", str(data), "-m", "immediate", "-w", "stop"])


def database_urls(connection, name):
    password, port = connection["password"], connection["port"]
    return (
        f"postgresql+psycopg://beront_migrator:{password}@127.0.0.1:{port}/{name}",
        f"postgresql+psycopg://beront_app:{password}@127.0.0.1:{port}/{name}",
    )


@contextlib.contextmanager
def test_database(server, *, migrate=True):
    name = "beront_test_" + uuid4().hex
    with psycopg.connect(**server, autocommit=True) as control:
        control.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    migration_url, runtime_url = database_urls(server, name)
    engine = create_engine(migration_url)
    try:
        if migrate:
            with engine.begin() as connection:
                command.upgrade(alembic_config(connection), "head")
                connection.exec_driver_sql("GRANT USAGE ON SCHEMA public TO beront_app")
                connection.exec_driver_sql("GRANT USAGE ON SCHEMA beront_api TO beront_app")
                connection.exec_driver_sql(
                    "GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA beront_api TO beront_app"
                )
                connection.exec_driver_sql("REVOKE ALL ON TABLE alembic_version FROM beront_app")
        yield migration_url, runtime_url, engine
    finally:
        engine.dispose()
        with psycopg.connect(**server, autocommit=True) as control:
            control.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))


@pytest.fixture(scope="session")
def postgres_server():
    with tempfile.TemporaryDirectory(prefix="beront-pg-tests-") as directory:
        with isolated_postgres(Path(directory)) as connection:
            yield connection


@pytest.fixture
def database(postgres_server):
    with test_database(postgres_server) as urls:
        yield urls


@pytest.fixture
def tmp_path():
    with tempfile.TemporaryDirectory(prefix="beront-case-") as directory:
        yield Path(directory)


@pytest.fixture
def settings(database, tmp_path):
    return Settings(
        database_url=database[1],
        secret_key=secrets.token_urlsafe(48),
        storage_root=tmp_path / "storage",
        testing=True,
        rate_limits=False,
    )


class FakeMailer:
    configured = True

    def __init__(self):
        self.sent = []

    def send(self, recipient, subject, body):
        self.sent.append({"to": recipient, "subject": subject, "body": body})


@pytest.fixture
def mailer():
    return FakeMailer()


@pytest.fixture
def app(settings, mailer):
    application = create_app(settings, mailer)
    yield application
    application.extensions["beront"].engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin(app):
    return app.extensions["beront"].identity.create_admin("test-admin", PASSWORD)


@pytest.fixture
def auth(client, admin):
    token = client.get("/api/v1/auth/csrf").json["data"]["csrf_token"]
    response = client.post(
        "/api/v1/auth/login",
        json={"username": admin.username, "password": PASSWORD},
        headers={"X-CSRFToken": token},
    )
    assert response.status_code == 200, response.json
    return {"X-CSRFToken": response.json["data"]["csrf_token"]}


@pytest.fixture
def reference_data(app, admin):
    catalog = app.extensions["beront"].catalog
    category = catalog.create_definition(
        "categories", {"slug": "niche", "name_es": "Nicho", "name_en": "Niche"}, admin.id
    )
    for slug in ("male", "female", "unisex"):
        catalog.create_definition(
            "audiences", {"slug": slug, "name_es": slug, "name_en": slug}, admin.id
        )
    from decimal import Decimal

    for kind, volume in (
        ("decant", "5"),
        ("decant", "10"),
        ("decant", "7.5"),
        ("full_bottle", "100"),
    ):
        catalog.create_definition(
            "presentations",
            {
                "kind": kind,
                "volume_ml": Decimal(volume),
                "name_es": volume + " ml",
                "name_en": volume + " ml",
            },
            admin.id,
        )
    return category


@pytest.fixture
def sample(app, admin, reference_data):
    service = app.extensions["beront"]
    brand = service.catalog.create_brand(
        {"name": "Casa de prueba", "category_id": reference_data["id"]}, admin.id
    )
    product = service.catalog.create_product(
        {
            "brand_id": brand.id,
            "name": "Perfume de prueba",
            "slug": "perfume-prueba",
            "audience": "unisex",
            "description_es": "Descripción de prueba.",
        },
        admin.id,
    )
    variants = []
    from decimal import Decimal

    for kind, volume, price in (
        ("decant", "5", "12.50"),
        ("decant", "10", "20.00"),
        ("full_bottle", "100", "120.00"),
    ):
        variants.append(
            service.catalog.create_variant(
                product.id,
                {
                    "kind": kind,
                    "volume_ml": Decimal(volume),
                    "price": Decimal(price),
                },
                admin.id,
            )
        )
    product = service.catalog.update_product(
        product.id, {"version": 1, "published": True}, admin.id
    )
    service.inventory.adjust(
        actor_id=admin.id,
        kind="decant",
        target_id=product.id,
        delta=Decimal("20"),
        version=1,
        reason="Saldo de prueba",
        operation_id=uuid4(),
    )
    service.inventory.adjust(
        actor_id=admin.id,
        kind="full_bottle",
        target_id=variants[2].id,
        delta=Decimal("2"),
        version=1,
        reason="Saldo de prueba",
        operation_id=uuid4(),
    )
    return product, variants
