import hashlib
from datetime import UTC, datetime
from uuid import uuid4

from beront.modules.inventory.domain.entities import Movement
from beront.modules.inventory.domain.policies import adjusted_balance
from beront.shared.domain.errors import Conflict, DomainError


class InventoryService:
    def __init__(self, uow_factory):
        self.uow_factory = uow_factory

    def list_balances(self, page=1, page_size=24):
        with self.uow_factory() as uow:
            return uow.stock.balances(page, page_size)

    def list_movements(self, page=1, page_size=24):
        with self.uow_factory() as uow:
            return uow.stock.movements(page, page_size)

    def adjust(
        self, *, actor_id, kind, target_id, delta, version, reason, operation_id, request_id=None
    ):
        if kind not in {"decant", "full_bottle"} or not reason.strip():
            raise DomainError("INVALID_ADJUSTMENT", "Indica tipo y motivo del ajuste.")
        fingerprint = hashlib.sha256(
            f"{kind}|{target_id}|{delta:.2f}|{version}|{reason}|{actor_id}".encode()
        ).hexdigest()
        with self.uow_factory() as uow:
            existing = uow.stock.movement(operation_id)
            if existing:
                return self._replay(existing, fingerprint)
            balance = uow.stock.balance(kind, target_id, lock=True)
            existing = uow.stock.movement(operation_id)
            if existing:
                return self._replay(existing, fingerprint)
            if balance.version != version:
                raise Conflict()
            balance.amount = adjusted_balance(kind, balance.amount, delta)
            uow.stock.save_balance(balance)
            movement = Movement(
                id=uuid4(),
                kind=kind,
                target_id=target_id,
                delta=delta,
                balance_after=balance.amount,
                version_after=balance.version,
                reason=reason,
                actor_id=actor_id,
                operation_id=operation_id,
                fingerprint=fingerprint,
                created_at=datetime.now(UTC),
            )
            uow.stock.add_movement(movement, balance.id)
            uow.audit(actor_id, "inventory.adjust", movement.id, request_id)
            uow.commit()
            return movement, True

    @staticmethod
    def _replay(existing, fingerprint):
        if existing.fingerprint != fingerprint:
            raise Conflict("OPERATION_CONFLICT", "La clave de operación ya se usó con otros datos.")
        return existing, False
