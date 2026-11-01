from datetime import datetime
from decimal import Decimal
from uuid import UUID

from beront.modules.inventory.domain.entities import Balance, Movement
from beront.shared.infrastructure.pg_call import require_record


def to_balance(row):
    return Balance(
        UUID(row["id"]), UUID(row["target_id"]), row["kind"], Decimal(row["amount"]), row["version"]
    )


def to_movement(row):
    values = {key: row[key] for key in Movement.__dataclass_fields__}
    for key in ("id", "target_id", "actor_id", "operation_id"):
        values[key] = UUID(values[key])
    for key in ("delta", "balance_after"):
        values[key] = Decimal(values[key])
    values["created_at"] = datetime.fromisoformat(values["created_at"])
    return Movement(**values)


class SqlStockRepository:
    def __init__(self, pg):
        self.pg = pg

    def ensure_decants(self, product_id):
        self.pg.call("inventory_ensure_decants", {"product_id": product_id})

    def ensure_bottles(self, variant_id):
        self.pg.call("inventory_ensure_bottles", {"variant_id": variant_id})

    def amounts(self, kind, target_ids):
        if not target_ids:
            return {}
        values = self.pg.call("inventory_amounts", {"kind": kind, "target_ids": target_ids})
        return {UUID(key): Decimal(value) for key, value in values.items()}

    def balance(self, kind, target_id, *, lock=False):
        return to_balance(
            require_record(
                self.pg.call(
                    "inventory_balance_get", {"kind": kind, "target_id": target_id, "lock": lock}
                )
            )
        )

    def save_balance(self, balance):
        balance.version = self.pg.call("inventory_balance_save", vars(balance))["version"]

    def movement(self, operation_id):
        row = self.pg.call("inventory_movement_get", {"operation_id": operation_id})
        return to_movement(row) if row else None

    def add_movement(self, movement, balance_id):
        self.pg.call("inventory_movement_add", {**vars(movement), "balance_id": balance_id})

    def balances(self, page, page_size):
        result = self.pg.call("inventory_balances", {"page": page, "page_size": page_size})
        return [to_balance(row) for row in result["items"]], result["total"]

    def movements(self, page, page_size):
        result = self.pg.call("inventory_movements", {"page": page, "page_size": page_size})
        return [to_movement(row) for row in result["items"]], result["total"]
