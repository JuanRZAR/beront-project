from typing import Annotated

from pydantic import Field

from beront.shared.presentation.schemas import Schema


class LoginBody(Schema):
    username: Annotated[str, Field(min_length=1, max_length=100)]
    password: Annotated[str, Field(min_length=1, max_length=128)]

    model_config = {"extra": "forbid", "str_strip_whitespace": False}
