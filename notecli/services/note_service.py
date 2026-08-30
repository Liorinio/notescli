from datetime import datetime
from typing import Union, Any, cast
import logging
from notecli.app_types.note_base import NoteBase
from notecli.app_types.note_registery import NOTE_INFO
from notecli.app_types.note_type import NoteType
from notecli.app_types.note_models import NoteSimple, NoteList, NoteBookMark
from notecli.memory_storage.db_schema import MemoryStorage
from notecli.metadata import common_metadata_dict, special_fields_dict
from notecli.exeptions import NotFoundError

logger = logging.getLogger(__name__)


def __create_note_by_type__(note_type: NoteType, title: str, content: Union[str, list[str]]) -> NoteSimple | NoteList | NoteBookMark:
    """
    Creates a note according to its type
    """
    note_class, expected_type, note_class_name = NOTE_INFO[note_type]

    if isinstance(content, expected_type):
        logger.info(f"A {note_class_name} note was created, layer: note_service")
        return note_class(title=title, note_type=note_type, content=content, creation_time=datetime.now())
    logger.error(f"Invalid type of content, required a {expected_type}")
    raise TypeError(f"The content must be a {expected_type}")


def __add_to_db__(new_note: NoteSimple | NoteList | NoteBookMark, db: MemoryStorage | None) -> None:
    """
    Adds the note to the memory "db"
    """
    if db is None:
        logger.error(f"The db doesn't exist, layer: note_service")
        raise BlockingIOError("None exist db")
    note_id = db.get_counter()
    db.update_counter_by_one()
    new_note.set_id(note_id)
    logger.info(f"Note number {note_id} is ready to be inserted to the database, layer: note_service")
    db.add_note_to_db(new_note)


def __parse_notes__(db: MemoryStorage | None) -> list[NoteBase]:
    """
    Gets list of all the notes from the memory db
    """
    if db is None:
        logger.error("The db doesn't exist, layer: note_service")
        return []
    return db.get_db_data()


def deleter(note_id: int, db: MemoryStorage | None) -> NoteBase:
    """
    Deletes a note from the memory db
    """
    if db is not None:
        removed_note = db.remove_note_from_db(note_id)
        if removed_note:
            logger.info(f"Note number {note_id} was deleted from the database, layer: note_service")
            return removed_note
        else:
            logger.warning("The note doesn't exist, layer: note_service")
            raise NotFoundError("Index not found")
    else:
        logger.error("The db doesn't exist, layer: note_service")
        raise BlockingIOError("None exist db")


def adder(note_type: NoteType, title: str, content: Union[str, list[str]], db: MemoryStorage | None) -> None:
    """
    Creates and adds a note to the memory db
    """
    note = __create_note_by_type__(note_type, title, content)
    __add_to_db__(note, db)


def get_all(db: MemoryStorage | None) -> None | str:
    """
    Returns all the notes, suitable for cli
    """
    if db is None:
        return None
    data = __parse_notes__(db)
    output = []
    for note in data:
        output.append(note.to_str())
    return "\n".join(output)


def retrieve_all_notes(db: MemoryStorage | None):
    """
    Returns all the notes, suitable for rest-api
    """
    if db is None:
        return None
    data = __parse_notes__(db)
    return {
        "notes":
            [note.to_str() for note in data]
    }


def show_note_structure() -> str:
    """
    Returns the structure of a note as a string, suitable for cli
    """
    output = ["The common fields between all the notes:"]
    for field in common_metadata_dict:
        description, expected_type = common_metadata_dict[field]
        output.append(f'Field: {field}, description: {description}, Type: {expected_type}, layer: note_service')
    for desc_str in special_fields_dict:
        output.append(desc_str)

    return "\n".join(output)


def get_note_structure() -> dict[str, dict[str, tuple[str, str]] | set[str]]:
    """
    Returns the structure of a note as a dict, suitable for rest-api
    """
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


def search_note_by_id(note_id: int, db: MemoryStorage) -> str | None:
    """
    Gets a note's id, and finds the note accordingly
    """
    try:
        returned_note = db.get_note_from_db_by_id(note_id)
        if returned_note is not None:
            logger.info(f"Note number {note_id} was found, layer: note_service")
            return returned_note.to_str()
    except NotFoundError:
        raise NotFoundError("Index doesn't exist")


def update_title_of_note(title: str, note_id: int, db: MemoryStorage) -> bool:
    """
    Gets content for update and note's id, and updates the note's content
    """
    try:
        returned_note = db.get_note_from_db_by_id(note_id)
        returned_note.set_title(title)
        returned_note.set_update_date()
        logger.info(f"Note number {note_id} was updated, layer: note_service")
        return True
    except NotFoundError:
        raise NotFoundError("Index wasn't found")


def update_content_of_note(content: str | list[str], note_id: int, db: MemoryStorage) -> bool:
    """
    Gets content for update and note's id, and updates the note's content
    """
    try:
        note = db.get_note_from_db_by_id(note_id)

        expected_type = (NOTE_INFO[note.note_type])[1]

        if isinstance(content, expected_type):
            cast(Any, note).set_content(content)
            note.set_update_date()
            logger.info(f"Note number {note_id} was updated, layer: note_service")
            return True

        logger.error("Invalid content type %s for note type %s, layer: note_service", type(content).__name__, type(note).__name__)
        return False
    except NotFoundError:
        raise NotFoundError("Index wasn't found")



def search_notes_by_date(early_creation_date: datetime, late_creation_date: datetime, db: MemoryStorage) -> list[NoteBase] | None:
    """
    Gets a range of dates, and finds the note accordingly
    """
    notes = db.get_notes_by_date(early_creation_date, late_creation_date)
    if notes is not None:
        logger.info(f"the notes were found, layer: note_service")
        return notes
    logger.warning(f"the notes weren't found, layer: note_service")
    return None


def search_note_by_date_and_title(early_creation_date: datetime, late_creation_date: datetime, db: MemoryStorage, title: str):
    """
    Gets a range of dates and title, and finds the note accordingly
    """
    notes = db.get_notes_by_date_and_title(early_creation_date, late_creation_date, title)
    if notes is not None:
        logger.info(f"Notes were found, layer: note_service")
        return [returned_note.to_str() for returned_note in notes]
    logger.warning(f"Notes weren't found, layer: note_service")
    return None


def show_content_url(note_id: int, db: MemoryStorage) -> tuple[int, Any] | None:
    """
    Gets an id of a note, and shows the response content of an http request of its url, if it is a bookMark note
    """
    try:
        note = db.get_note_from_db_by_id(note_id)

        if not isinstance(note, NoteBookMark):
            logger.warning(f"Note number {note_id} is not in the right type, layer: note_service")
            return None

        return note.open_url()
    except NotFoundError:
        raise NotFoundError("not wasn't found")
