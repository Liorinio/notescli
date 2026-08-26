from datetime import datetime
from typing import Literal
from pydantic import BaseModel

#classes for creating the "NOT IMPLEMENTED" functions
#This is their only use
#The use of pydantic here is for the validation of the fields
class NoteCreateRequest(BaseModel):
    type: str
    title: str
    text: str | None
    list: list[str] | None
    url: str | None
    tags: list[str] | None

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
    type: Literal["simple"]
    title: str | None = None
    text: str | None = None
    tags: list[str] | None


class ListNoteUpdateRequest(BaseModel):
    type: Literal["list"]
    title: str | None
    list: list[str] | None
    tags: list[str] | None


class BookmarkNoteUpdateRequest(BaseModel):
    type: Literal["bookmark"]
    title: str | None = None
    url: str | None = None


NoteUpdateRequest = SimpleNoteUpdateRequest | ListNoteUpdateRequest | BookmarkNoteUpdateRequest