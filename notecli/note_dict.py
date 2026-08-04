from typing import Any


class NoteDict:
    db_data: list[dict[str, Any]]
    counter: int

    def __init__(self, db_data: list[dict[str, Any]], counter: int):
        self.db_data = db_data
        self.counter = counter



