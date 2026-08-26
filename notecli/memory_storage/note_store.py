from notecli.app_types.NoteBase import NoteBase
from notecli.database.tables import Counter
from typing import TypedDict


# An object that is used for parsing from Postgres to the "memory db"
class NoteStore(TypedDict):
    db_data: list[NoteBase]
    counter: Counter

