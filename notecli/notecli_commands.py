from datetime import datetime
from typing import Union, get_type_hints, Any
import logging
from notecli.app_types.NoteBase import NoteBase
from notecli.app_types.NoteRegistery import NOTE_INFO
from notecli.app_types.NoteType import NoteType
from notecli.app_types.NoteModels import NoteSimple, NoteList, NoteBookMark
from notecli.memory_storage.db_schema import Db

logger = logging.getLogger(__name__)


def __create_note_by_type__(note_type: NoteType, title: str, content: Union[str, list[str]]) -> NoteSimple | NoteList | NoteBookMark:
    note_class, expected_type, note_class_name = NOTE_INFO[note_type]

    if not isinstance(content, expected_type):
        logger.error(f"Invalid type of content, required a {expected_type}")
        raise TypeError(f"The content must be a {expected_type}")
    logger.info(f"A {note_class_name} note was created")
    return note_class(title=title, note_type=note_type, content=content, creation_time=datetime.now())


def __add_to_db__(new_data: NoteSimple | NoteList | NoteBookMark, db: Db | None) -> None:
    if db is None:
        logger.error(f"The db doesn't exist")
        raise BlockingIOError("None exist db")
    note_id = db.get_counter()
    db.update_counter_by_one()
    new_data.set_id(note_id)
    logger.info(f"Note number {note_id} is ready to be inserted to the database")
    db.add_note_to_db(new_data)


def __parse_notes__(db: Db | None) -> list[NoteBase]:
    if db is None:
        logger.error("The db doesn't exist")
        return []
    return db.get_db_data()


def delete_note(note_id: int, db: Db | None) -> NoteBase:
    if db is not None:
        removed_note = db.remove_note_from_db(note_id)
        if removed_note:
            logger.info(f"Note number {note_id} was deleted from the database")
            return removed_note
    logger.error("The db doesn't exist")
    raise BlockingIOError("None exist db")


def adder(note_type: NoteType, title: str, content: Union[str, list[str]], db: Db | None) -> None:
    note = __create_note_by_type__(note_type, title, content)
    __add_to_db__(note, db)


def print_all(db: Db | None) -> None:
    if db is not None:
        data = __parse_notes__(db)
        for note in data:
            print(note.to_str())


def show_note_structure() -> None:
    hints = get_type_hints(NoteBase)
    print("The common fields between all the notes:")
    for field, field_type in hints.items():
        print(f"Field: {field} | Type: {field_type.__name__}")

    print("\nNoteSimple has the following field as well:")
    print("Field: content | Type: str")

    print("\nNoteBookMark has the following field as well:")
    print("Field: content_site_url | Type: str")

    print("\nNoteList has the following field as well:")
    print("Field: content | Type: list[str]")


def search_note_by_id(note_id: int, db: Db) -> str | None:
    returned_note = db.get_note_from_db_by_id(note_id)
    if returned_note is not None:
        logger.info(f"Note number {note_id} was found")
        return returned_note.to_str()
    else:
        return None


def update_note_title(title: str, note_id: int, db: Db) -> None:
    returned_note = db.get_note_from_db_by_id(note_id)
    if returned_note is not None:
        returned_note.set_title(title)
        returned_note.set_update_date()
        logger.info(f"Note number {note_id} was updated")
    else:
        logger.warning(f"Note number {note_id} wasn't updated")


def update_note_content(content: str | list[str] | None, note_id: int, db: Db) -> None:
    note = db.get_note_from_db_by_id(note_id)

    if note is None:
        logger.warning("Note with id %s not found", note_id)
        return

    if isinstance(content, str):
        if isinstance(note, (NoteSimple, NoteBookMark)):
            note.set_content(content)
            note.set_update_date()
            logger.info(f"Note number {note_id} was updated")
            return

    elif isinstance(content, list):
        if isinstance(note, NoteList):
            note.set_content(content)
            note.set_update_date()
            logger.info(f"Note number {note_id} was updated")
            return

    logger.warning("Invalid content type %s for note type %s", type(content).__name__, type(note).__name__)


def search_notes_by_date(early_creation_date: datetime, late_creation_date: datetime, db: Db) -> list[NoteBase] | None:
    notes = db.get_notes_by_date(early_creation_date, late_creation_date)
    if notes is not None:
        logger.info(f"the notes were found")
        return notes
    else:
        logger.warning(f"the notes were found")
        return None


def search_note_by_date_and_id(early_creation_date: datetime, late_creation_date: datetime, db: Db, note_id: int) -> str | None:
    note = db.get_notes_by_date_and_id(early_creation_date, late_creation_date, note_id)
    if note is not None:
        logger.info(f"Note number {note_id} was found")
        return note.to_str()
    else:
        logger.warning(f"Note number {note_id} wasn't found")
        return None


def show_content_url(note_id: int, db: Db) ->tuple[int, Any] | None:
    note = db.get_note_from_db_by_id(note_id)

    if note is None:
        logger.warning(f"Note number {note_id} wasn't found")
        return None

    if not isinstance(note, NoteBookMark):
        logger.warning(f"Note number {note_id} is not in the right type")
        return None

    return note.open_url()