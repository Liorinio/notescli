from typing import Union, get_type_hints
import logging
from notecli.app_types.NoteBase import NoteBase
from notecli.app_types.NoteRegistery import NOTE_INFO
from notecli.app_types.NoteType import NoteType
from notecli.app_types.NoteModels import NoteSimple, NoteList, NoteBookMark
from notecli.db_schema import Db

logger = logging.getLogger(__name__)


def __create_note_by_type__(note_type: NoteType, title: str,
                            content: Union[str, list[str]]) -> NoteSimple | NoteList | NoteBookMark:
    note_class, expected_type, note_class_name = NOTE_INFO[note_type]

    if not isinstance(content, expected_type):
        logger.error(f"Invalid type of content, required a {expected_type}")
        raise TypeError(f"The content must be a {expected_type}")
    logger.info(f"A {note_class_name} note was created")
    return note_class(title=title, note_type=note_type, content=content)


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
        logger.info(f"Note number {note_id} was deleted from the database")
        return removed_note
    logger.error("The db doesn't exist")
    raise BlockingIOError("None exist db")


def adder(note_type: NoteType, title: str, content: Union[str, list[str]], db: Db | None):
    note = __create_note_by_type__(note_type, title, content)
    __add_to_db__(note, db)


def print_all(db: Db | None) -> None:
    if db is not None:
        data = __parse_notes__(db)
        for note in data:
            print(note.to_str())


def show_note_structure():
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



