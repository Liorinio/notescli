from datetime import datetime
from typing import Optional

from requests import HTTPError

from notecli.app_types.note_type import NoteType
from notecli.database.database_manager import PostgresDb
from notecli.memory_storage.db_schema import MemoryStorage
from notecli.services.note_service import adder, search_note_by_date_and_title, search_note_by_id, \
    update_content_of_note, update_title_of_note, show_content_url, get_all, deleter
from notecli.exceptions.not_found_exception import NotFoundError


def add_note(given_note_type: str, title: str, content: list[str] | str|  None, db: MemoryStorage | None):
    """
    Adds a note to db
    """
    if db is None:
        return None
    note_type = NoteType[given_note_type.upper()]

    if content is None:
        return None

    if note_type not in (NoteType.SIMPLE, NoteType.BOOKMARK):
        content_to_add: list[str] = content
    else:
        if type(content) is not str:
            raise ValueError(f"{note_type.name} notes require exactly one content value")
        content_to_add: str = content

    added_note = adder(note_type, title, content_to_add, db)
    PostgresDb.save_to_db(db.parse_to_dict())
    return added_note


def delete_note(note_id: int, db: MemoryStorage | None):
    """
    Deletes a note from the db
    """
    try:
        if db is None:
            return
        removed_note = deleter(note_id, db)
        PostgresDb.save_to_db(db.parse_to_dict(), removed_note.note_id)
    except NotFoundError:
        raise NotFoundError("Note doesn't exist")


def get_all_notes(db: MemoryStorage | None):
    """
    Lists the notes from db
    """
    list_of_notes = get_all(db)
    if list_of_notes is None:
        return None
    return list_of_notes


def search_note(early_creation_date: datetime, late_creation_date: datetime | None, title: str | None, db: MemoryStorage | None):
    """
    Searches a note in the db by its title and a range of dates
    """
    if db is None:
        return None
    returned_notes = search_note_by_date_and_title(early_creation_date, late_creation_date, db, title)
    if returned_notes is None:
        return None
    else:
        return returned_notes


def view_specific_note(note_id: int, db: MemoryStorage | None):
    """
    Views a note
    """
    try:
        if db is None:
            return None
        returned_description = search_note_by_id(note_id, db)
        if returned_description is None:
            return None
        else:
            return returned_description
    except NotFoundError:
        raise NotFoundError("Note doesn't exist")


def navigate_url(note_id: int, db: MemoryStorage | None):
    """
    Get a note's id and gets its http request output (if it is a bookmark note)
    """
    try:
        if db is None:
            return None
        returned_output = show_content_url(note_id, db)
        if returned_output is None:
            return None
        else:
            return returned_output[0], returned_output[1]
    except NotFoundError:
        raise NotFoundError("Note wasn't found")
    except HTTPError:
        raise HTTPError("Can't open a url for note type that isn't bookmark")


def update_title(title: str | None, note_id: int, db: MemoryStorage | None):
    """
    Updates the title of a note based on the note's id
    """
    if db is None:
        return False
    if title is None:
        return False
    is_updated = update_title_of_note(title, note_id, db)
    PostgresDb.save_to_db(db.parse_to_dict())
    return is_updated


def update_content(content: str | list[str] | None, note_id: int, db: MemoryStorage | None):
    """
    Updates the content of a note based on the note's id
    """
    if db is None:
        return False
    if content is None:
        return False
    is_updated = update_content_of_note(content, note_id, db)
    PostgresDb.save_to_db(db.parse_to_dict())
    return is_updated


def update_note(note_id: int, db: MemoryStorage | None, title: Optional[str], content: Optional[str | list[str]]) -> bool:
    """
    Updates the title and the content of a note based on the note's id
    """
    if db is None:
        return False
    is_title_updated = False
    is_content_updated = False

    if title is not None:
        try:
            is_title_updated = update_title_of_note(title, note_id, db)
        except NotFoundError:
            raise NotFoundError("Note wasn't found")

    if content is not None:
        try:
            is_content_updated = update_content_of_note(content, note_id, db)
        except NotFoundError:
            raise NotFoundError("Note wasn't found")

    if is_title_updated or is_content_updated:
        PostgresDb.save_to_db(db.parse_to_dict())
        return True
    else:
        return False
