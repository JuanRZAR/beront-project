from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from beront.shared.domain.errors import Conflict


def test_createsuperuser_cli_creates_only_one_owner(app):
    runner = app.test_cli_runner()
    password = "Temporary owner password 12345"
    result = runner.invoke(
        args=["createsuperuser"], input="owner\n" + password + "\n" + password + "\n"
    )
    assert result.exit_code == 0, result.output
    second = runner.invoke(
        args=["createsuperuser"], input="second\n" + password + "\n" + password + "\n"
    )
    assert second.exit_code != 0
    assert "administrador" in second.output


def test_concurrent_cli_service_requests_cannot_create_two_owners(app, database):
    ready = Barrier(2)

    def create(name):
        ready.wait(timeout=10)
        try:
            app.extensions["beront"].identity.create_admin(name, "Temporary owner password 12345")
            return True
        except Conflict:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(create, ["first", "second"])) == [False, True]
    with database[2].connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM administrators")) == 1


def test_database_enforces_single_owner_even_outside_cli(admin, database):
    with database[2].begin() as connection:
        with pytest.raises(IntegrityError):
            connection.execute(
                text(
                    "INSERT INTO administrators(id,username,password_hash,active,singleton_slot) VALUES(gen_random_uuid(),'second','test',true,1)"
                )
            )


def test_last_variant_of_published_perfume_cannot_be_disabled(client, auth, sample):
    product, variants = sample
    for variant in variants[:-1]:
        assert (
            client.patch(
                "/api/v1/admin/variants/" + str(variant.id),
                json={"version": 1, "active": False},
                headers=auth,
            ).status_code
            == 200
        )
    result = client.patch(
        "/api/v1/admin/variants/" + str(variants[-1].id),
        json={"version": 1, "active": False},
        headers=auth,
    )
    assert result.status_code == 422
    assert result.json["error"]["code"] == "PRODUCT_NOT_READY"
