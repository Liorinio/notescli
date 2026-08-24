from datetime import datetime
from typing import Union, Any, cast
import logging
from notecli.app_types.NoteBase import NoteBase
from notecli.app_types.NoteRegistery import NOTE_INFO
from notecli.app_types.NoteType import NoteType
from notecli.app_types.NoteModels import NoteSimple, NoteList, NoteBookMark
from notecli.memory_storage.db_schema import Db
from notecli.metadata import common_metadata_dict, special_fields_dict

logger = logging.getLogger(__name__)


def __create_note_by_type__(note_type: NoteType, title: str,
                            content: Union[str, list[str]]) -> NoteSimple | NoteList | NoteBookMark:
    note_class, expected_type, note_class_name = NOTE_INFO[note_type]

    if isinstance(content, expected_type):
        logger.info(f"A {note_class_name} note was created")
        return note_class(title=title, note_type=note_type, content=content, creation_time=datetime.now())
    logger.error(f"Invalid type of content, required a {expected_type}")
    raise TypeError(f"The content must be a {expected_type}")


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


def deleter(note_id: int, db: Db | None) -> NoteBase:
    if db is not None:
        removed_note = db.remove_note_from_db(note_id)
        if removed_note:
            logger.info(f"Note number {note_id} was deleted from the database")
            return removed_note
        else:
            logger.warning("The note doesn't exist")
            raise ValueError("None exist index in the database")
    else:
        logger.error("The db doesn't exist")
        raise BlockingIOError("None exist db")


def adder(note_type: NoteType, title: str, content: Union[str, list[str]], db: Db | None) -> None:
    note = __create_note_by_type__(note_type, title, content)
    __add_to_db__(note, db)


def get_all(db: Db | None) -> None | str:
    if db is None:
        return None
    data = __parse_notes__(db)
    output = []
    for note in data:
        output.append(note.to_str())
    return "\n".join(output)


def retrieve_all_notes(db: Db | None):
    if db is None:
        return None
    data = __parse_notes__(db)
    return {
        "notes":
            [note.to_str() for note in data]
    }


def show_note_structure() -> str:
    output = ["The common fields between all the notes:"]
    for field in common_metadata_dict:
        description, expected_type = common_metadata_dict[field]
        output.append(f'Field: {field}, description: {description}, Type: {expected_type}')
    for desc_str in special_fields_dict:
        output.append(desc_str)

    return "\n".join(output)


def get_note_structure() -> dict[str, dict[str, tuple[str, str]] | set[str]]:
    return {
        "common fields": {
            field: (
                common_metadata_dict[field][0],
                common_metadata_dict[field][1]
            )
            for field in common_metadata_dict
        },
        "NoteSimple": {
            special_fields_dict[0]
        },
        "NoteBookMark": {
            special_fields_dict[0]
        },
        "NoteList": {
            special_fields_dict[2]
        }
    }


def search_note_by_id(note_id: int, db: Db) -> str | None:
    returned_note = db.get_note_from_db_by_id(note_id)
    if returned_note is not None:
        logger.info(f"Note number {note_id} was found")
        return returned_note.to_str()
    return None


def update_title_of_note(title: str, note_id: int, db: Db) -> bool:
    returned_note = db.get_note_from_db_by_id(note_id)
    if returned_note is None:
        logger.warning(f"Note number {note_id} wasn't updated")
        return False
    else:
        returned_note.set_title(title)
        returned_note.set_update_date()
        logger.info(f"Note number {note_id} was updated")
        return True


def update_content_of_note(content: str | list[str], note_id: int, db: Db) -> bool:
    note = db.get_note_from_db_by_id(note_id)

    if note is None:
        logger.warning("Note with id %s not found", note_id)
        return False

    expected_type = (NOTE_INFO[note.note_type])[1]

    if isinstance(content, expected_type):
        cast(Any, note).set_content(content)
        note.set_update_date()
        logger.info(f"Note number {note_id} was updated")
        return True

    logger.warning("Invalid content type %s for note type %s", type(content).__name__, type(note).__name__)
    return False


def search_notes_by_date(early_creation_date: datetime, late_creation_date: datetime, db: Db) -> list[NoteBase] | None:
    notes = db.get_notes_by_date(early_creation_date, late_creation_date)
    if notes is not None:
        logger.info(f"the notes were found")
        return notes
    logger.warning(f"the notes were found")
    return None


def search_note_by_date_and_title(early_creation_date: datetime, late_creation_date: datetime, db: Db, title: str):
    notes = db.get_notes_by_date_and_title(early_creation_date, late_creation_date, title)
    if notes is not None:
        logger.info(f"Notes were found")
        return [returned_note.to_str() for returned_note in notes]
    logger.warning(f"Notes weren't found")
    return None


def show_content_url(note_id: int, db: Db) -> tuple[int, Any] | None:
    note = db.get_note_from_db_by_id(note_id)

    if note is None:
        logger.warning(f"Note number {note_id} wasn't found")
        return None

    if not isinstance(note, NoteBookMark):
        logger.warning(f"Note number {note_id} is not in the right type")
        return None

    return note.open_url()
