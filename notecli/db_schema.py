import logging
from datetime import datetime, timedelta
from typing import Self
from notecli.note_store import NoteStore
from notecli.app_types.NoteBase import NoteBase

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

    def parse_to_dict(self) -> NoteStore:
        logger.info("The database is ready to be saved")
        return NoteStore([note for note in self.db_data], self.counter)

    def parse_from_dict(self, data_dict: NoteStore) -> Self:
        self.db_data = []
        notes_counter = 0

        for note in data_dict.db_data:
            note.set_id(notes_counter)
            self.db_data.append(note)
            notes_counter += 1

        self.counter = data_dict.counter

        logger.info("The database was parsed and it is in the memory")

        return self

    def get_note_from_db_by_id(self, note_id: int) -> NoteBase | None:
        for note in self.db_data:
            if note.note_id == note_id:
                return note

        logger.warning("There is no such id in the database")
        return None

    def remove_note_from_db(self, note_id: int) -> NoteBase | None:
        if not self.db_data:
            return None
        else:
            for i in range(len(self.db_data)):
                if i == note_id:
                    logger.info(f"Note number {note_id} was found")
                    return self.db_data.pop(note_id)

            logger.warning("There is no such id in the database")
            return None

    def get_notes_by_date(self, early_creation_date: datetime, late_creation_date: datetime) -> list[NoteBase] | None:
        return [note for note in self.db_data if early_creation_date <= note.get_creation_date() <= late_creation_date]

    def get_notes_by_date_and_id(self, early_creation_date: datetime, late_creation_date: datetime,
                                 note_id: int) -> NoteBase | None:
        late_creation_date += timedelta(seconds=1)

        return next((note for note in self.db_data if (
                early_creation_date <= note.get_creation_date() < late_creation_date and note.note_id == note_id)),
                    None)
