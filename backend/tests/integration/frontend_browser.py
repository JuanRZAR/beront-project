import json
import logging
import os
import runpy
import secrets
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from PIL import Image
from werkzeug.serving import make_server

from beront.app import create_app
from beront.config import Settings

PROJECT = Path(__file__).resolve().parents[3]
FRONTEND = PROJECT / "frontend"


def free_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def bun_binary():
    if configured := os.environ.get("BUN_BIN"):
        return configured
    found = shutil.which("bun.exe") or shutil.which("bun.cmd") or shutil.which("bun")
    if not found:
        raise RuntimeError("Bun no está disponible.")
    candidate = Path(found).parent / "node_modules" / "bun" / "bin" / "bun.exe"
    return str(candidate) if candidate.is_file() else found


class DiscardingMailer:
    configured = True

    def send(self, recipient, subject, body):
        return None


def seed_commerce(container, admin):
    actor = admin.id
    catalog, commerce, orders = container.catalog, container.commerce, container.orders
    category = catalog.create_definition(
        "categories", {"slug": "arabic", "name_es": "Árabe", "name_en": "Arabic"}, actor
    )
    for slug, es, en in (
        ("female", "Mujer", "Women"),
        ("male", "Hombre", "Men"),
        ("unisex", "Unisex", "Unisex"),
    ):
        catalog.create_definition("audiences", {"slug": slug, "name_es": es, "name_en": en}, actor)
    for kind, volume in (("decant", "5"), ("decant", "7.5"), ("full_bottle", "100")):
        catalog.create_definition(
            "presentations",
            {
                "kind": kind,
                "volume_ml": Decimal(volume),
                "name_es": volume + " ml",
                "name_en": volume + " ml",
            },
            actor,
        )
    brand = catalog.create_brand({"name": "Casa E2E", "category_id": category["id"]}, actor)
    product = catalog.create_product(
        {"brand_id": brand.id, "name": "Perfume E2E", "slug": "perfume-e2e", "audience": "unisex"},
        actor,
    )
    catalog.create_variant(
        product.id, {"kind": "decant", "volume_ml": Decimal("5"), "price": Decimal("12.50")}, actor
    )
    catalog.update_product(product.id, {"version": 1, "published": True}, actor)
    container.inventory.adjust(
        actor_id=actor,
        kind="decant",
        target_id=product.id,
        delta=Decimal("50"),
        version=1,
        reason="Saldo de pruebas",
        operation_id=uuid4(),
    )
    commerce.save_settings(
        {
            "version": 0,
            "whatsapp_number": "",
            "terms_es": "Términos de prueba",
            "terms_en": "Test terms",
        },
        actor,
    )
    province = commerce.create(
        "provinces", {"code": "17", "name": "Pichincha", "mainland": True}, actor
    )
    commerce.create(
        "cities",
        {"province_id": province["id"], "name": "Quito", "shipping_fee": Decimal("5.25")},
        actor,
    )
    commerce.create(
        "banks",
        {
            "bank_name": "Banco de pruebas",
            "account_type": "Cuenta de pruebas",
            "account_number": "000123",
            "holder_name": "Titular de pruebas",
            "holder_identification": "0000000000",
        },
        actor,
    )
    statuses = {}
    for slug, es, en, phase, purpose in (
        (
            "transfer",
            "Pago en revisión",
            "Payment under review",
            "awaiting_payment",
            "bank_transfer",
        ),
        ("whatsapp", "Pago por WhatsApp", "Pay via WhatsApp", "awaiting_payment", "whatsapp"),
        ("issue", "Pago sin existencias", "Payment without stock", "stock_issue", "stock_issue"),
        ("paid", "Preparando envío", "Preparing shipment", "paid", None),
        ("shipped", "Enviado", "Shipped", "shipped", None),
        ("delivered", "Entregado", "Delivered", "delivered", None),
        ("cancelled", "Cancelado", "Cancelled", "cancelled", None),
    ):
        statuses[slug] = orders.create_definition(
            "statuses",
            {"slug": slug, "name_es": es, "name_en": en, "phase": phase, "purpose": purpose},
            actor,
        )
    for start, end in (
        ("transfer", "paid"),
        ("whatsapp", "paid"),
        ("transfer", "issue"),
        ("whatsapp", "issue"),
        ("issue", "paid"),
        ("transfer", "cancelled"),
        ("whatsapp", "cancelled"),
        ("paid", "shipped"),
        ("shipped", "delivered"),
    ):
        orders.create_definition(
            "transitions",
            {"from_status_id": statuses[start]["id"], "to_status_id": statuses[end]["id"]},
            actor,
        )


def main():
    helpers = runpy.run_path(str(PROJECT / "backend" / "tests" / "conftest.py"))
    with tempfile.TemporaryDirectory(prefix="beront-browser-") as directory:
        temporary = Path(directory)
        with (
            helpers["isolated_postgres"](temporary) as server,
            helpers["test_database"](server) as database,
        ):
            api_port, frontend_port = free_port(), free_port()
            base_url = f"http://127.0.0.1:{frontend_port}"
            app = create_app(
                Settings(
                    database_url=database[1],
                    secret_key=secrets.token_urlsafe(48),
                    frontend_origin=base_url,
                    storage_root=temporary / "storage",
                    testing=True,
                    rate_limits=False,
                ),
                DiscardingMailer(),
            )
            username, password = "browser-test", secrets.token_urlsafe(24)
            admin = app.extensions["beront"].identity.create_admin(username, password)
            seed_commerce(app.extensions["beront"], admin)
            logging.getLogger("werkzeug").setLevel(logging.WARNING)
            image = temporary / "image.png"
            Image.new("RGB", (30, 40), "#B8A58A").save(image)
            http = make_server("127.0.0.1", api_port, app, threaded=True)
            thread = threading.Thread(target=http.serve_forever, daemon=True)
            thread.start()
            environment = {
                **os.environ,
                "BACKEND_URL": f"http://127.0.0.1:{api_port}",
                "BERONT_E2E_BASE_URL": base_url,
                "BERONT_E2E_USERNAME": username,
                "BERONT_E2E_PASSWORD": password,
                "BERONT_E2E_IMAGE": str(image),
                "ASTRO_TELEMETRY_DISABLED": "1",
            }
            process = None
            try:
                with (temporary / "frontend.log").open("wb") as log:
                    process = subprocess.Popen(
                        [bun_binary(), "run", "dev", "--port", str(frontend_port)],
                        cwd=FRONTEND,
                        env=environment,
                        stdin=subprocess.DEVNULL,
                        stdout=log,
                        stderr=log,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                    )
                    ready = False
                    for _ in range(100):
                        try:
                            with urllib.request.urlopen(base_url + "/es/", timeout=2) as response:
                                ready = response.status == 200
                            if ready:
                                break
                        except (OSError, urllib.error.URLError):
                            time.sleep(0.2)
                        if process.poll() is not None:
                            break
                    if not ready:
                        raise RuntimeError("No se pudo iniciar el frontend de pruebas.")
                    result = subprocess.run(
                        [bun_binary(), "x", "--bun", "playwright", "test"],
                        cwd=FRONTEND,
                        env=environment,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                        check=False,
                    )
                    report = FRONTEND / "test-results" / "application-report.json"
                    if report.is_file():
                        stats = json.loads(report.read_text(encoding="utf-8"))["stats"]
                        print(
                            "Browser checks:",
                            stats["expected"],
                            "passed;",
                            stats["unexpected"],
                            "failed.",
                        )
                    return result.returncode
            finally:
                if process is not None and process.poll() is None:
                    if os.name == "nt":
                        subprocess.run(
                            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            check=False,
                            creationflags=subprocess.CREATE_NO_WINDOW,
                        )
                    else:
                        process.terminate()
                    process.wait(timeout=10)
                http.shutdown()
                http.server_close()
                thread.join(timeout=5)
                app.extensions["beront"].engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
