from notecli.app_types.NoteBase import NoteBase


class NoteStore:
    db_data: list[NoteBase]
    counter: int

    def __init__(self, db_data: list[NoteBase], counter: int):
        self.db_data = db_data
        self.counter = counter

    def get_db_data(self) -> list[NoteBase]:
        return self.db_data

    def get_counter(self) -> int:
        return self.counter



