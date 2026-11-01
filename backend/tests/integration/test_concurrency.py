from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier
from uuid import uuid4

from beront.shared.domain.errors import Conflict


def test_simultaneous_adjustments_cannot_overwrite_stock(app, admin, sample):
    product, _ = sample
    service = app.extensions["beront"].inventory
    ready = Barrier(2)

    def adjust():
        ready.wait(timeout=10)
        try:
            return service.adjust(
                actor_id=admin.id,
                kind="decant",
                target_id=product.id,
                delta=Decimal("-15"),
                version=2,
                reason="Ajuste concurrente de prueba",
                operation_id=uuid4(),
            )[1]
        except Conflict:
            return False

    with ThreadPoolExecutor(max_workers=2) as workers:
        results = list(workers.map(lambda _: adjust(), range(2)))
    assert sorted(results) == [False, True]
    with app.extensions["beront"].uow_factory() as uow:
        assert uow.stock.balance("decant", product.id).amount == Decimal("5")


def test_simultaneous_retries_apply_one_movement(app, admin, sample):
    product, _ = sample
    service = app.extensions["beront"].inventory
    ready, operation_id = Barrier(2), uuid4()

    def adjust():
        ready.wait(timeout=10)
        return service.adjust(
            actor_id=admin.id,
            kind="decant",
            target_id=product.id,
            delta=Decimal("-5"),
            version=2,
            reason="Reintento concurrente de prueba",
            operation_id=operation_id,
        )

    with ThreadPoolExecutor(max_workers=2) as workers:
        results = list(workers.map(lambda _: adjust(), range(2)))
    assert sorted(created for _, created in results) == [False, True]
    assert results[0][0].id == results[1][0].id
    with app.extensions["beront"].uow_factory() as uow:
        assert uow.stock.balance("decant", product.id).amount == Decimal("15")
        assert uow.stock.movements(1, 24)[1] == 3
