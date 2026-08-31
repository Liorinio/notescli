import logging
from datetime import datetime, timedelta
from typing import Self
from notecli.memory_storage.note_store import NoteStore
from notecli.app_types.note_base import NoteBase
from notecli.database.tables import Counter
from notecli.exceptions.not_found_exception import NotFoundError

logger = logging.getLogger(__name__)


class MemoryStorage:
    db_data: list[NoteBase]


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
        logger.info("The note was inserted to the database, layer: memory_storage")

    def parse_to_dict(self) -> NoteStore:
        logger.info("The database is ready to be saved, layer: memory_storage")
        return NoteStore(db_data=[note for note in self.db_data], counter=Counter(id=1, counter=self.counter))

    def parse_from_dict(self, data_dict: NoteStore) -> Self:
        self.db_data = []
        notes_counter = 0

        for note in data_dict["db_data"]:
            note.set_id(notes_counter)
            self.db_data.append(note)
            notes_counter += 1

        self.counter = data_dict["counter"].counter

        logger.info("The database was parsed and it is in the memory, layer: memory_storage")

        return self

    def get_note_from_db_by_id(self, note_id: int) -> NoteBase:
        for note in self.db_data:
            if note.note_id == note_id:
                return note

        logger.error("There is no such id in the database, layer: memory_storage")
        raise NotFoundError("Index not found")

    def remove_note_from_db(self, note_id: int) -> NoteBase :
        if self.db_data:
            for i in range(len(self.db_data)):
                if self.db_data[i].note_id == note_id:
                    logger.info(f"Note number {note_id} was found, layer: memory_storage")
                    return self.db_data.pop(note_id)

            logger.error("There is no such id in the database, layer: memory_storage")
            raise NotFoundError("Index not found")
        else:
            logging.error("The database is empty, layer: memory_storage")
            raise ValueError("Database is empty or no records found, layer: memory_storage")

    def get_notes_by_date(self, early_creation_date: datetime, late_creation_date: datetime) -> list[NoteBase] | None:
        list_of_required_notes: list[NoteBase] = [note for note in self.db_data if early_creation_date <= note.get_creation_date() <= late_creation_date]
        logger.info("Notes retrieved, layer: memory_storage")
        return list_of_required_notes

    def get_notes_by_date_and_id(self, early_creation_date: datetime, late_creation_date: datetime, note_id: int) -> NoteBase | None:
        late_creation_date += timedelta(seconds=1)

        required_note: NoteBase | None = next((note for note in self.db_data if (early_creation_date <= note.get_creation_date() < late_creation_date and note.note_id == note_id)),None)
        logger.info("Notes retrieved, layer: memory_storage")
        return required_note

    def get_notes_by_date_and_title(self, early_creation_date: datetime, late_creation_date: datetime, title: str) -> list[NoteBase] | None:
        late_creation_date += timedelta(seconds=1)

        list_of_required_notes: list[NoteBase] = [note for note in self.db_data if (early_creation_date <= note.get_creation_date() < late_creation_date and note.title == title)]
        logger.info("Notes retrieved, layer: memory_storage")
        return list_of_required_notes

    def get_notes_by_title(self, title: str):
        list_of_required_notes: list[NoteBase] = [note for note in self.db_data if note.title == title]
        logger.info("Notes retrieved, layer: memory_storage")
        return list_of_required_notes
