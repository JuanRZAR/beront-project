"""Medición local reproducible con la semilla y una base PostgreSQL temporal."""

import argparse
import json
import math
import runpy
import secrets
import statistics
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter

from beront.app import create_app
from beront.cli import load_seed_module
from beront.config import Settings
from beront.modules.catalog.application.import_seed import ImportCatalogSeed
from beront.modules.commerce.application.seed_home import SeedHomeMessages
from beront.shared.infrastructure.pg_call import PgCall

BACKEND = Path(__file__).resolve().parents[2]


def measure(app, path, iterations):
    samples, sizes = [], []
    calls = Counter()
    original = PgCall.call

    def counted(self, name, values=None):
        calls[name] += 1
        return original(self, name, values)

    with app.test_client() as client:
        for _ in range(2):
            assert client.get(path).status_code == 200
        PgCall.call = counted
        try:
            for _ in range(iterations):
                started = perf_counter()
                response = client.get(path)
                samples.append((perf_counter() - started) * 1000)
                assert response.status_code == 200, response.json
                sizes.append(len(response.data))
        finally:
            PgCall.call = original
    samples.sort()
    return {
        "median_ms": round(statistics.median(samples), 2),
        "p95_ms": round(samples[math.ceil(len(samples) * 0.95) - 1], 2),
        "bytes": round(statistics.mean(sizes)),
        "pg_calls_per_request": sum(calls.values()) / iterations,
        "pg_calls": {name: count / iterations for name, count in sorted(calls.items())},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=20)
    args = parser.parse_args()
    if not 5 <= args.iterations <= 100:
        parser.error("iterations debe estar entre 5 y 100")
    helpers = runpy.run_path(str(BACKEND / "tests" / "conftest.py"))
    with tempfile.TemporaryDirectory(prefix="beront-benchmark-") as directory:
        root = Path(directory)
        with (
            helpers["isolated_postgres"](root) as server,
            helpers["test_database"](server) as database,
        ):
            app = create_app(
                Settings(
                    database_url=database[1],
                    secret_key=secrets.token_urlsafe(48),
                    storage_root=root / "storage",
                    testing=True,
                    rate_limits=False,
                    cart_requires_stock=False,
                )
            )
            services = app.extensions["beront"]
            try:
                services.identity.create_admin("benchmark", secrets.token_urlsafe(32))
                seed = load_seed_module()
                imported = ImportCatalogSeed(services.uow_factory, services.media).execute(
                    seed.load_source(), lambda name: (seed.SOURCE / "imagenes" / name).open("rb")
                )
                SeedHomeMessages(services.uow_factory).execute()
                paths = {
                    "catalog": "/api/v1/catalog/products?kind=decant",
                    "facets": "/api/v1/catalog/facets",
                    "home": "/api/v1/home/messages",
                }
                result = {
                    "products": imported["imported"],
                    "iterations": args.iterations,
                    "warmups": 2,
                    "endpoints": {
                        name: measure(app, path, args.iterations) for name, path in paths.items()
                    },
                }

                def request(_):
                    with app.test_client() as client:
                        return client.get(paths["catalog"]).status_code

                started = perf_counter()
                with ThreadPoolExecutor(max_workers=4) as executor:
                    statuses = list(executor.map(request, range(40)))
                elapsed = perf_counter() - started
                result["concurrent_catalog"] = {
                    "workers": 4,
                    "requests": len(statuses),
                    "errors": sum(status != 200 for status in statuses),
                    "requests_per_second": round(len(statuses) / elapsed, 2),
                }
                args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
                print(json.dumps(result, indent=2))
            finally:
                services.engine.dispose()


if __name__ == "__main__":
    main()
