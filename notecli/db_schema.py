import logging
from typing import Self
from notecli.note_dict import NoteDict
from notecli.app_types.NoteBase import NoteBase
from notecli.app_types.NoteRegistery import NOTE_INFO
from notecli.app_types.NoteType import NoteType

logger = logging.getLogger(__name__)

class Db:
    db_data: list[NoteBase]
    counter: int

    def __init__(self):
        self.db_data = []
        self.counter = 0

    def get_counter(self) -> int:
        return self.counter

    def set_counter(self, value: int) -> None:
        self.counter = value

    def update_counter_by_one(self) -> None:
        self.counter += 1

    def get_db_data(self) -> list[NoteBase]:
        return self.db_data

    def set_db_data(self, data: list[NoteBase]) -> None:
        self.db_data = data

    def add_note_to_db(self, note: NoteBase) -> None:
        self.db_data.append(note)
        logger.info("The note was inserted to the database")

    def parse_to_dict(self) -> NoteDict:
        db_note_dict = NoteDict([note.serialize() for note in self.db_data], self.counter)
        logger.info("The database is ready to be saved")
        return db_note_dict

    def parse_from_dict(self, data_dict: NoteDict) -> Self:
        self.db_data = []

        for note_data in data_dict.db_data:
            note_type: NoteType = NoteType(note_data["note_type"])
            note_class = NOTE_INFO[note_type][0]

            note = note_class(title="",note_type=note_type,content=note_data.get("content", "")).deserialize(note_data)
            self.db_data.append(note)

        self.counter = data_dict.counter
        logger.info("The database was parsed and it is in the memory")
        return self
