from notecli.app_types.NoteBase import NoteBase
from notecli.database.tables import Counter

# An object that is used for parsing from Postgres to the "memory db"
class NoteStore:
    db_data: list[NoteBase]
    counter: Counter

    def __init__(self, db_data: list[NoteBase], counter: Counter):
        self.db_data = db_data
        self.counter = counter

    def get_db_data(self) -> list[NoteBase]:
        return self.db_data

    def get_counter(self) -> int:
        return self.counter.counter
