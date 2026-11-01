from collections import defaultdict
from decimal import Decimal

from beront.modules.inventory.domain.policies import BottleStockPolicy, DecantStockPolicy

POLICIES = {"decant": DecantStockPolicy, "full_bottle": BottleStockPolicy}


class StockAvailability:
    def __init__(self, repository):
        self.repository = repository

    def inspect(self, requirements, *, aggregate=False):
        targets = {"decant": set(), "full_bottle": set()}
        required = defaultdict(lambda: Decimal("0"))
        keys = {}
        for item in requirements:
            target = item.product_id if item.kind == "decant" else item.variant_id
            targets[item.kind].add(target)
            key = (item.kind, target) if aggregate else (item.kind, item.variant_id)
            keys[item.variant_id] = (key, target)
            required[key] += POLICIES[item.kind].required(item.volume_ml, item.quantity)
        amounts = {kind: self.repository.amounts(kind, list(ids)) for kind, ids in targets.items()}
        return {
            item.variant_id: amounts[item.kind].get(keys[item.variant_id][1], Decimal("0"))
            >= required[keys[item.variant_id][0]]
            for item in requirements
        }
