from datetime import datetime
from enum import Enum

class NoteType(Enum):
    SIMPLE = 1
    LISTNOTE = 2
    BOOKMARK = 3

# a type that describes a dict that describes the notes are built
type serializedDict = dict[str, int|str|NoteType|datetime|list[str]]

