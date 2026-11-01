from typing import Annotated

from pydantic import Field

from beront.shared.presentation.schemas import PageQuery, PatchSchema, Schema


class MediaQuery(PageQuery):
    q: Annotated[str, Field(max_length=120)] = ""


class MediaUpload(Schema):
    name: Annotated[str, Field(max_length=250)] = ""


class MediaPatch(PatchSchema):
    name: Annotated[str, Field(max_length=250)]
