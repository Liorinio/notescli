from typing import TypedDict

from app_types.NoteModels import NoteSimple, NoteBookMark, NoteList
from app_types.NoteType import NoteType

# schemas for de-serializing the notes from the db
class NoteData(TypedDict):
    note_id: int
    title: str
    note_type: NoteType
    created_at: str
    updated_at: str

class BookMarkData(NoteData):
    content_site_url: str

class SimpleData(NoteData):
    content: str

class ListData(NoteData):
    content: list[str]

type unionOfData = SimpleData| ListData | BookMarkData

NOTE_INFO : dict[NoteType, tuple[type[NoteSimple], type[str], str] | tuple[type[NoteBookMark], type[str], str] | tuple[type[NoteList], type[list], str]] = {
    NoteType.SIMPLE: (NoteSimple, str, "Simple"),
    NoteType.BOOKMARK: (NoteBookMark, str, "BookMark"),
    NoteType.LISTNOTE: (NoteList, list, "List")
}