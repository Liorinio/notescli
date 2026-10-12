from datetime import datetime
from pydantic import BaseModel
from typing import Any, Optional, TypedDict, List
from notecli.app_types.note_models import NoteBookMark, NoteSimple, NoteList
from notecli.memory_storage.db_schema import MemoryStorage


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
    sort_type: str | None
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
    text: Optional[str]
    list: Optional[List[str]]
    url: Optional[str]
    note_type : NoteSimple | NoteBookMark | NoteList

class MetadatNoteParams(TypedDict):
    pass

class QueueResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None
