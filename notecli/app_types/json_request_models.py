from pydantic import BaseModel, HttpUrl, field_validator
from typing import List, Optional
from notecli.app_types.note_type import NoteType

# Pydantic Models for JSON Request Bodies
class NoteRequest(BaseModel):
    type: NoteType
    title: str
    text: Optional[str] = None
    list: Optional[List[str]] = None
    url: Optional[HttpUrl] = None

    @field_validator("type", mode="before")
    @classmethod
    def parse_string_to_enum(cls, value):
        if isinstance(value, str):
            mapping: dict[str, int] = {"simple": 1, "listnote": 2, "bookmark": 3}
            val_lower: str = value.lower()
            if val_lower in mapping:
                return mapping[val_lower]
            raise ValueError("Type must be 'simple', 'listnote', or 'bookmark'")
        return value

class NoteCreate(NoteRequest):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": 1,
                    "title": "My First Note",
                    "text": "Hello world!"
                }
            ]
        }
    }

    @field_validator("type", mode="before")
    @classmethod
    def parse_string_to_enum(cls, value):
        return super().parse_string_to_enum(value)


class NoteUpdate(NoteRequest):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "My First Note",
                    "text": "Hello world!",
                    "list": ["hello", "world!"],
                    "url": "https://fastapi.tiangolo.com"
                }
            ]
        }
    }

    @field_validator("type", mode="before")
    @classmethod
    def parse_string_to_enum(cls, value):
        return super().parse_string_to_enum(value)