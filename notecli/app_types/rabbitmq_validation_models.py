from datetime import datetime
from pydantic import BaseModel
from typing import Any, Optional, TypedDict, List
from notecli.app_types.note_models import NoteBookMark, NoteSimple, NoteList

class QueueRequest(BaseModel):
    action: str
    params: dict = {}

class AddNoteParams(TypedDict):
    given_note_type: str
    title: str
    content: list[str] | str | None

class DeleteNoteParams(TypedDict):
    note_id: int

class GetAllNotesParams(TypedDict):
    sort_type: str | None

class SearchNoteParams(TypedDict):
    early_creation_date: datetime | None
    late_creation_date: datetime | None
    title: str | None

class ViewNoteParams(TypedDict):
    note_id: int

class NavigateNoteParams(TypedDict):
    note_id: int

class UpdateNoteParams(TypedDict):
    note_id: int
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
