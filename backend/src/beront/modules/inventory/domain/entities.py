from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class Balance:
    id: UUID
    target_id: UUID
    kind: str
    amount: Decimal
    version: int


@dataclass
class Movement:
    id: UUID
    kind: str
    target_id: UUID
    delta: Decimal
    balance_after: Decimal
    version_after: int
    reason: str
    actor_id: UUID
    operation_id: UUID
    fingerprint: str
    created_at: datetime
