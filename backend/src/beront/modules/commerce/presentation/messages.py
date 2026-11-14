from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, StrictBool, StrictInt

from beront.shared.presentation.schemas import CatalogKey, Identifier, Schema, Version

Text = Annotated[str, Field(min_length=1, max_length=180)]


class MessageText(Schema):
    eyebrow: Text
    title: Text
    emphasis: Annotated[str, Field(max_length=180)] = ""
    body: Annotated[str, Field(min_length=1, max_length=1000)]
    primary_label: Annotated[str, Field(min_length=1, max_length=80)]
    secondary_label: Annotated[str, Field(max_length=80)] = ""


class MessageContent(Schema):
    es: MessageText
    en: MessageText


class MessageCreate(Schema):
    slug: CatalogKey
    content: MessageContent
    primary_path: Annotated[str, Field(min_length=1, max_length=250)]
    secondary_path: Annotated[str, Field(max_length=250)] = ""
    icon: Literal["bottle", "truck", "whatsapp", "tag"] = "bottle"
    stats_kind: Literal["none", "decant", "full_bottle"] = "none"
    position: Annotated[StrictInt, Field(ge=0, le=1000)] = 0
    active: StrictBool = False
    starts_at: AwareDatetime | None = None
    ends_at: AwareDatetime | None = None
    image_ids: Annotated[list[Identifier], Field(max_length=3)] = []


class MessageSave(MessageCreate):
    version: Version
