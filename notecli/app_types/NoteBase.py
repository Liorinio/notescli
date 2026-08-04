from datetime import datetime
from typing import Self
from notecli.app_types.NoteType import NoteType, serializedDict

class NoteBase:
    note_id: int
    title: str
    note_type: NoteType
    created_at: datetime
    updated_at: datetime

    def __init__(self, title: str, note_type: NoteType):
        self.title = title
        self.note_type = note_type
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.note_id = -1

    def to_str(self) -> str:
        return (
            f'note_id: {self.note_id}, '
            f'title: {self.title}, '
            f'note_type: {self.note_type.name}, '
            f'created_at: {self.created_at}, '
            f'updated_at: {self.updated_at}'
        )

    def serialize(self) -> serializedDict:
        return {
            "note_id": self.note_id,
            "title": self.title,
            "note_type": self.note_type.value,
             "created_at": (
            self.created_at.isoformat()
            if hasattr(self.created_at, "isoformat")
            else self.created_at
        ),
        "updated_at": (
            self.updated_at.isoformat()
            if hasattr(self.updated_at, "isoformat")
            else self.updated_at
        )
        }

    def set_id(self, given_note_id: int):
        self.note_id = given_note_id

    def deserialize(self, data: dict) -> Self:
        raw_id = data.get("note_id")
        if isinstance(raw_id, int):
            self.note_id = raw_id

        raw_title = data.get("title")
        if isinstance(raw_title, str):
            self.title = raw_title

        raw_note_type = data.get("note_type")
        if isinstance(raw_note_type, str):
            try:
                self.note_type = NoteType(raw_note_type)
            except ValueError:
                pass

        raw_created_at = data.get("created_at")
        if isinstance(raw_created_at, str):
            try:
                self.created_at = datetime.fromisoformat(raw_created_at)
            except ValueError:
                pass

        raw_updated_at = data.get("updated_at")
        if isinstance(raw_updated_at, str):
            try:
                self.updated_at = datetime.fromisoformat(raw_updated_at)
            except ValueError:
                pass

        return self