from datetime import UTC

from beront.shared.domain.values import decimal_text


def balance_data(balance):
    return {
        "id": str(balance.id),
        "target_id": str(balance.target_id),
        "kind": balance.kind,
        "amount": decimal_text(balance.amount),
        "version": balance.version,
        "unit": "ml" if balance.kind == "decant" else "units",
    }


def movement_data(movement):
    return {
        "id": str(movement.id),
        "kind": movement.kind,
        "target_id": str(movement.target_id),
        "delta": decimal_text(movement.delta),
        "balance_after": decimal_text(movement.balance_after),
        "version_after": movement.version_after,
        "reason": movement.reason,
        "actor_id": str(movement.actor_id),
        "operation_id": str(movement.operation_id),
        "created_at": movement.created_at.astimezone(UTC).isoformat(),
    }
