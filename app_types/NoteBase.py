from datetime import datetime
from typing import Self
from pydantic import BaseModel
from src.app_types.NoteSchemas import NoteData, unionOfData
from src.app_types.NoteType import NoteType, serializedDict

class NoteBase(BaseModel):
    note_id: int
    title: str
    note_type: NoteType
    created_at: datetime
    updated_at: datetime

    def to_str(self) -> str:
        return (
            f'note_id: {self.note_id}, '
            f'title: {self.title}, '
            f'note_type: {self.note_type.name}, '
            f'created_at: {self.created_at}, '
            f'updated_at: {self.updated_at}'
        )

    def serialize(self) -> serializedDict:
        return self.model_dump(mode="json")

    def set_id(self, given_note_id: int):
        self.note_id = given_note_id

    @classmethod
    def deserialize(cls, data: NoteData | unionOfData) -> Self:
        return cls.model_validate(data)