from pydantic import BaseModel
from typing import Any, Optional, TypedDict

class QueueRequest(BaseModel):
    action: str
    params: dict = {}

'''
class AddUserParams(TypedDict):
    username: str
    age: int
    '''
class AddNoteParams(TypedDict):
    given_note_type: str
    title: str
    content: list[str] | str | None
    db: MemoryStorage | None

class DeleteNoteParams(TypedDict):
    note_id: int
    db: MemoryStorage | None

class GetAllNotesParams(TypedDict):
    db: MemoryStorage | None

class SearchNoteParams(TypedDict):
    early_creation_date: datetime | None
    late_creation_date: datetime | None
    title: str | None
    db: MemoryStorage | None

class ViewNoteParams(TypedDict):
    note_id: int
    db: MemoryStorage | None

class NavigateNoteParams(TypedDict):
    note_id: int
    db: MemoryStorage | None

class UpdateNoteParams(TypedDict):
    note_id: int
    db: MemoryStorage | None
    title: Optional[str]
    content: Optional[str | list[str]]

class QueueResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None
