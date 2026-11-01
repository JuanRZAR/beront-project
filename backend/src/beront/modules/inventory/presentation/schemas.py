from typing import Annotated

from pydantic import Field

from beront.shared.presentation.schemas import DecimalInput, Identifier, Kind, Schema, Version


class AdjustmentBody(Schema):
    kind: Kind
    target_id: Identifier
    delta: DecimalInput
    version: Version
    reason: Annotated[str, Field(min_length=1, max_length=300)]
    operation_id: Identifier
