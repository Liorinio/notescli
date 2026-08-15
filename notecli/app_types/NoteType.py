from datetime import datetime
from enum import Enum
from typing import TypedDict


class NoteType(Enum):
    SIMPLE = 1
    LISTNOTE = 2
    BOOKMARK = 3


# a type that describes a dict that describes the notes are built
type serializedDict = dict[str, int | str | NoteType | datetime | list[str]]


class SerializedNote(TypedDict):
    note_id: int
    title: str
    note_type: str
    created_at: str
    updated_at: str


class SerializedNoteSimple(SerializedNote):
    content: str


class SerializedNoteBookMark(SerializedNote):
    content: str


class SerializedNoteList(SerializedNote):
    tags: list[str]


type union_of_serialized_notes = SerializedNoteSimple | SerializedNoteBookMark | SerializedNoteList
