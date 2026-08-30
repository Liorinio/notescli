from pydantic import BaseModel, HttpUrl, field_validator
from typing import List, Optional
from notecli.app_types.NoteType import NoteType

# Pydantic Models for JSON Request Bodies
class NoteCreate(BaseModel):
    type: NoteType
    title: str
    text: Optional[str] = None
    list: Optional[List[str]] = None
    url: Optional[HttpUrl] = None

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
        if isinstance(value, str):
            mapping = {"simple": 1, "listnote": 2, "bookmark": 3}
            val_lower = value.lower()
            if val_lower in mapping:
                return mapping[val_lower]
            raise ValueError("Type must be 'simple', 'listnote', or 'bookmark'")
        return value


class NoteUpdate(BaseModel):
    type: NoteType
    title: Optional[str] = None
    text: Optional[str] = None
    list: Optional[List[str]] = None
    url: Optional[HttpUrl] = None

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
        if isinstance(value, str):
            mapping = {"simple": 1, "listnote": 2, "bookmark": 3}
            val_lower = value.lower()
            if val_lower in mapping:
                return mapping[val_lower]
            raise ValueError("Type must be 'simple', 'listnote', or 'bookmark'")
        return value