from notecli.app_types.NoteType import NoteType
from datetime import datetime
from typing import Literal, List
from pydantic import BaseModel, Field


#classes for creating the "NOT IMPLEMENTED" functions
#This is their only use
#The use of pydantic here is for the validation of the fields

class NoteCreateRequest(BaseModel):
    type: str
    title: str
    text: str | None = None
    list: List[str] | None = None
    url: str | None = None
    tags: List[str] | None = None

class NotePlaceHolder(BaseModel):
    note_id: int
    title: str
    note_type: str
    created_at: datetime
    updated_at: datetime

class Pagination(BaseModel):
    page: int
    limit: int
    total: int

class NotePage(BaseModel):
    data: list[NotePlaceHolder]
    pagination: Pagination

class SimpleNoteUpdateRequest(BaseModel):
    type: Literal[NoteType.SIMPLE]
    title: str | None = None
    text: str | None = None
    tags: List[str] | None = None

class ListNoteUpdateRequest(BaseModel):
    type: Literal[NoteType.LISTNOTE]
    title: str | None = None
    list: List[str] | None = None
    tags: List[str] | None = None

class BookmarkNoteUpdateRequest(BaseModel):
    type: Literal[NoteType.BOOKMARK]
    title: str | None = None
    url: str | None = None

NoteUpdateRequest =SimpleNoteUpdateRequest | ListNoteUpdateRequest | BookmarkNoteUpdateRequest