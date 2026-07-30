from datetime import datetime
from pydantic import BaseModel
from app_types.NoteData import NoteData, unionOfData
from app_types.NoteType import NoteType, serializedDict, SerializedNote


class NoteBase(BaseModel):
    note_id: int
    title: str
    note_type: NoteType
    created_at: datetime
    updated_at: datetime

    def to_str(self) -> str:
        return (
            f'note_id: {self.note_id} '
            f'title: {self.title} '
            f'note_type: {self.note_type.name} '
            f'created_at: {self.created_at} '
            f'updated_at: {self.updated_at} '
        )

    def serialize(self) -> serializedDict:
        return {
            'note_id': self.note_id,
            'title': self.title,
            'note_type': self.note_type.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    @classmethod
    def deserialize(cls, data: SerializedNote) -> "NoteBase":
        return NoteBase(
            note_id=data['note_id'],
            title=data['title'],
            note_type=NoteType[data['note_type']],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )