from typing import Annotated

from pydantic import Field

from beront.shared.presentation.schemas import (
    DecimalInput,
    Identifier,
    Kind,
    PageQuery,
    Schema,
    Version,
)


class BalanceQuery(PageQuery):
    kind: Kind | None = None
    q: Annotated[str, Field(max_length=120)] = ""


class AdjustmentBody(Schema):
    kind: Kind
    target_id: Identifier
    delta: DecimalInput
    version: Version
    reason: Annotated[str, Field(min_length=1, max_length=300)]
    operation_id: Identifier
