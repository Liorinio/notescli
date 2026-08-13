from datetime import datetime
from typing import Optional

from notecli.app_types.NoteType import NoteType
from notecli.database.FileManager import PostgresDb
from notecli.memory_storage.db_schema import Db
from notecli.notecli_commands import adder, show_note_structure, search_note_by_date_and_id, search_note_by_id, \
    update_content_of_note, update_title_of_note, show_content_url, print_all


def add_note(given_note_type: str, title: str, content: list[str], db: Db | None):
    if db is not None:
        note_type = NoteType[given_note_type]

        if note_type in (NoteType.SIMPLE, NoteType.BOOKMARK):
            if len(content) != 1:
                raise ValueError(f"{note_type.name} notes require exactly one content value")
            content_to_add = content[0]
        else:
            content_to_add = content

        adder(note_type, title, content_to_add, db)
        PostgresDb.save_to_db(db.parse_to_dict())

def delete_note(note_id: int, db: Db | None):
    if db is not None:
        delete_note(note_id, db)
        PostgresDb.save_to_db(db.parse_to_dict())


def show_notes_structure():
    show_note_structure()

def print_all_notes(db: Db | None):
    print_all(db)


def search_note(early_creation_date: datetime, late_creation_date: datetime,note_id: int, db:Db | None):
    if db is not None:
        returned_note = search_note_by_date_and_id(early_creation_date,late_creation_date, db, note_id)
        if returned_note is not None:
            print(returned_note)
        else:
            print("None")


def view_note(note_id: int, db: Db | None):
    if db is not None:
        returned_description = search_note_by_id(note_id, db)
        if returned_description is not None:
            print(returned_description)
        else:
            print("None")

def navigate_url(note_id: int, db: Db | None):
    if db is not None:
        returned_output = show_content_url(note_id, db)
        if returned_output is not None:
            print(returned_output[0])
            print(returned_output[1])
        else:
            print("None")

def update_title(title: str, note_id: int,  db: Db | None):
    if db is not None:
        update_title_of_note(title, note_id, db)
        PostgresDb.save_to_db(db.parse_to_dict())

def update_content(content: list[str], note_id: int,  db: Db | None):
    if db is not None:
        update_content_of_note(content, note_id, db)
        PostgresDb.save_to_db(db.parse_to_dict())

def update_note(note_id: int,  db: Db | None, title: Optional[str], content: Optional[str]):
    if db is not None:
        if title:
            update_title_of_note(title, note_id, db)

        if content:
            update_content_of_note(content, note_id, db)

        if title or content:
            PostgresDb.save_to_db(db.parse_to_dict())
        else:
            print("None")
