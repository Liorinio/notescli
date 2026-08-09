import logging
from datetime import datetime
from typing import Optional

import typer
from notecli.app_types.NoteType import NoteType
from notecli.db_schema import Db
from notecli.notecli_commands import adder, print_all, delete_note, show_note_structure, search_note_by_date_and_id, search_note_by_id, show_content_url, update_note_title, update_note_content
from notecli.FileManager import DbFileStorage

app = typer.Typer()
note_app = typer.Typer()
app.add_typer(note_app, name="note")
db: Db | None = None

logging.basicConfig(level = logging.INFO, format='%(levelname)s: %(message)s')

@app.callback()
def main():
    global db
    db = Db()
    db = db.parse_from_dict(DbFileStorage.load_from_json())

@note_app.command(name="list")
def list_notes():
    """
    prints all the notes that are in the database
    """
    print_all(db)

@note_app.command()
def add(given_note_type: str, title: str, content: list[str]):
    """
    :param given_note_type: The type of the given note (simple/bookmark/list), needs to be a string
    :param title: The title of the given note, needs to be a string
    :param content: The content of the note, needs to be a string or list of strings, for adding a simple or bookmark note, enter only one 'word' as the content
    adds a note to the database
    """
    if db is not None:
        note_type: NoteType = NoteType[given_note_type]
        adder(note_type, title, content, db)
        DbFileStorage.save_to_db(db.parse_to_dict())

@note_app.command()
def delete(note_id: int):
    """
    :param note_id: The id of the note, needs to be an integer
    deletes a note from the database
    """
    if db is not None:
        delete_note(note_id, db)
        DbFileStorage.save_to_db(db.parse_to_dict())

@note_app.command()
def show_structure():
    """
    shows the structure of the notes that are available for usage in the system
    """
    show_note_structure()

@note_app.command()
def search(early_creation_date: datetime, late_creation_date: datetime,note_id: int):
    """
    :param early_creation_date: The date which the note was created. needs to be a datetime type
    :param late_creation_date: The date which the note was updated. needs to be a datetime type
    :param note_id: The id of the note, needs to be an integer
    searches and prints a specific note
    """
    if db is not None:
        returned_note = search_note_by_date_and_id(early_creation_date,late_creation_date, db, note_id)
        if returned_note is not None:
            print(returned_note)
        else:
            print("None")


@note_app.command(name="view")
def view_note(note_id: int):
    """
    :param note_id: The id of the note, needs to be an integer
    shows a specific note
    """
    if db is not None:
        returned_description = search_note_by_id(note_id, db)
        if returned_description is not None:
            print(returned_description)
        else:
            print("None")

@note_app.command()
def navigate(note_id: int):
    """
    :param note_id: The id of the note, needs to be an integer
    shows the content of the url, if the note is a BookMarkNote
    """
    if db is not None:
        returned_output = show_content_url(note_id, db)
        if returned_output is not None:
            print(returned_output[0])
            print(returned_output[1])
        else:
            print("None")

@note_app.command()
def update_title(title: str, note_id: int):
    """
    :param title: The title of the given note, needs to be a string
    :param note_id: The id of the note, needs to be an integer
    updates the title of a specific note
    """
    if db is not None:
        update_note_title(title, note_id, db)
        DbFileStorage.save_to_db(db.parse_to_dict(), "db2.json")

@note_app.command()
def update_content(content: list[str], note_id: int):
    """
    :param content: The content of the note, needs to be a string or list of strings, for adding a simple or bookmark note, enter only one 'word' as the content
    :param note_id: The id of the note, needs to be an integer
    updates the content of a specific note
    """
    if db is not None:
        update_note_content(content, note_id, db)
        DbFileStorage.save_to_db(db.parse_to_dict(), "db2.json")

@note_app.command()
def update(note_id: int,title: Optional[str] = typer.Argument(None),content: Optional[str] = typer.Argument(None)):
    """
    :param note_id: The id of the note, needs to be an integer
    :param title: The title of the given note needs to be a string (an optional parameter)
    :param content: The content of the note, needs to be a string or list of strings, for adding a simple or bookmark note, enter only one 'word' as the content (an optional parameter)
    updates the content and/or the title of a specific note
    """
    if db is not None:
        if content and not title:
            update_note_content(content, note_id, db)
            DbFileStorage.save_to_db(db.parse_to_dict(), "db2.json")
        elif title and not content:
            update_note_title(title, note_id, db)
            DbFileStorage.save_to_db(db.parse_to_dict(), "db2.json")
        elif title and content:
            update_note_title(title, note_id, db)
            update_note_content(content, note_id, db)
            DbFileStorage.save_to_db(db.parse_to_dict(), "db2.json")
        else:
            print("None")

if __name__ == "__main__":
    app()