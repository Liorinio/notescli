from datetime import datetime
from typing import TypedDict
from app_types.NoteType import NoteType


class NoteData(TypedDict):
    note_id: int
    title: str
    note_type: NoteType
    created_at: datetime
    updated_at: datetime

class BookMarkData(NoteData):
    content_site_url: str

class SimpleData(NoteData):
    content: str

class ListData(NoteData):
    content: list[str]

type unionOfData = SimpleData| ListData | BookMarkData