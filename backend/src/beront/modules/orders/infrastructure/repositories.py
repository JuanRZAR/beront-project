from beront.shared.domain.errors import Conflict, DomainError
from beront.shared.infrastructure.pg_call import require_record


class SqlOrderRepository:
    RESOURCES = {"statuses": "status", "transitions": "transition"}

    def __init__(self, pg):
        self.pg = pg

    def lock_operation(self, operation_id):
        self.pg.call("orders_operation_lock", {"operation_id": operation_id})

    def get(self, identifier, *, lock=False):
        return require_record(self.pg.call("orders_get", {"id": identifier, "lock": lock}))

    def by_operation(self, operation_id):
        return self.pg.call("orders_get", {"operation_id": operation_id})

    def by_code(self, code_hash):
        return require_record(self.pg.call("orders_get", {"code_hash": code_hash}))

    def add(self, data):
        self.pg.call("orders_add", data)

    def save(self, data):
        return self.pg.call("orders_save", data)

    def history(self, order_id, status, actor_id):
        self.pg.call(
            "orders_history_add",
            {"order_id": order_id, "status_id": status["id"], "actor_id": actor_id},
        )

    def receipt(self, order_id, asset_id, actor_id):
        self.pg.call(
            "orders_receipt_add", {"order_id": order_id, "asset_id": asset_id, "actor_id": actor_id}
        )

    def status(self, identifier=None, *, purpose=None):
        result = self.pg.call("orders_status_get", {"id": identifier, "purpose": purpose})
        if not result:
            raise DomainError(
                "CHECKOUT_NOT_CONFIGURED", "Configura y activa los estados iniciales del pedido."
            )
        return result

    def transition(self, start, end):
        if not self.pg.call(
            "orders_transition_get", {"from_status_id": start, "to_status_id": end}
        ):
            raise Conflict(
                "INVALID_TRANSITION", "Esta transición no está habilitada en la configuración."
            )

    def listing(self, query):
        return self.pg.call("orders_list", query)

    def definitions(self, resource):
        return self.pg.call("orders_" + self.RESOURCES[resource] + "_list")

    def add_definition(self, resource, data):
        return self.pg.call("orders_" + self.RESOURCES[resource] + "_add", data)

    def save_definition(self, resource, identifier, data):
        return self.pg.call(
            "orders_" + self.RESOURCES[resource] + "_save", {**data, "id": identifier}
        )

    def recover(self, cedula, ip_hash, cooldown_seconds):
        return self.pg.call(
            "orders_recovery_request",
            {"cedula": cedula, "ip_hash": ip_hash, "cooldown_seconds": cooldown_seconds},
        )
