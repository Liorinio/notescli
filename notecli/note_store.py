from typing import Any


class NoteStore:
    db_data: list[dict[str, Any]]
    counter: int

    def __init__(self, db_data: list[dict[str, Any]], counter: int):
        self.db_data = db_data
        self.counter = counter

    def get_db_data(self) -> list[dict[str, Any]]:
        return self.db_data

    def get_counter(self) -> int:
        return self.counter



