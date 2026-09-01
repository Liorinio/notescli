from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator
from notecli.app_types.note_type import NoteType


class NoteBaseRequest(BaseModel):
    type: NoteType

    @field_validator("type", mode="before")
    @classmethod
    def parse_string_to_enum(cls, value):
        if isinstance(value, str):
            mapping = {"simple": 1, "listnote": 2, "bookmark": 3}
            value_lower = value.lower()

            if value_lower in mapping:
                return mapping[value_lower]

            raise ValueError("Type must be 'simple', 'listnote', or 'bookmark'")
        return value


class NoteCreate(NoteBaseRequest):
    title: str = Field(..., min_length=1, max_length=255)
    text: Optional[str] = Field(default=None, min_length=1)
    list: Optional[List[str]] = Field(default=None, min_length=1)
    url: Optional[HttpUrl] = None

    @model_validator(mode="after")
    def validate_content(self):
        if self.type == NoteType.SIMPLE and self.text is None:
            raise ValueError("Simple notes require text")
        if self.type == NoteType.LISTNOTE and self.list is None:
            raise ValueError("List notes require list")
        if self.type == NoteType.BOOKMARK and self.url is None:
            raise ValueError("Bookmark notes require url")

        return self


class NoteUpdate(NoteBaseRequest):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    text: Optional[str] = Field(default=None, min_length=1)
    list: Optional[List[str]] = Field(default=None, min_length=1)
    url: Optional[HttpUrl] = None


# A dictionary of content fields that should and shouldn't exist for each note_type
# The first two content fields shouldn't be, and the third one should
NOTE_CREATE_FIELDS = {
    NoteType.SIMPLE: ("list", "url", "text"),
    NoteType.LISTNOTE: ("text", "url", "list"),
    NoteType.BOOKMARK: ("text", "list", "url")
}
