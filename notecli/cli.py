import logging
from datetime import datetime
from typing import Optional
import typer
from notecli.memory_storage.db_schema import Db
from notecli.database.FileManager import PostgresDb
from notecli.services.notes_commands import add_note, delete_note, view_note, navigate_url, update_note, search_note, update_content, update_title, show_notes_structure, print_all_notes

app = typer.Typer()
note_app = typer.Typer()
app.add_typer(note_app, name="note")
db: Db | None = None

logging.basicConfig(level = logging.INFO, format='%(levelname)s: %(message)s')

@app.callback()
def main():
    global db
    db = Db()
    db = db.parse_from_dict(PostgresDb.load_from_db())

@note_app.command(name="list")
def list_notes():
    """
    prints all the notes that are in the database
    """
    print_all_notes(db)

@note_app.command()
def add(given_note_type: str, title: str, content: list[str]):
    """
    :param given_note_type: The type of the given note (simple/bookmark/list), needs to be a string
    :param title: The title of the given note, needs to be a string
    :param content: The content of the note, needs to be a string or list of strings, for adding a simple or bookmark note, enter only one 'word' as the content
    adds a note to the database
    """

    add_note(given_note_type, title, content, db)

@note_app.command()
def delete(note_id: int):
    """
    :param note_id: The id of the note, needs to be an integer
    deletes a note from the database
    """
    delete_note(note_id, db)

@note_app.command()
def show_structure():
    """
    shows the structure of the notes that are available for usage in the system
    """
    show_notes_structure()

@note_app.command()
def search(early_creation_date: datetime, late_creation_date: datetime,note_id: int):
    """
    :param early_creation_date: The date which the note was created. needs to be a datetime type
    :param late_creation_date: The date which the note was updated. needs to be a datetime type
    :param note_id: The id of the note, needs to be an integer
    searches and prints a specific note
    """
    search_note(early_creation_date,late_creation_date, note_id, db)


@note_app.command(name="view")
def view_note(note_id: int):
    """
    :param note_id: The id of the note, needs to be an integer
    shows a specific note
    """
    view_note(note_id, db)

@note_app.command()
def navigate(note_id: int):
    """
    :param note_id: The id of the note, needs to be an integer
    shows the content of the url, if the note is a BookMarkNote
    """
    navigate_url(note_id, db)

@note_app.command()
def update_title(title: str, note_id: int):
    """
    :param title: The title of the given note, needs to be a string
    :param note_id: The id of the note, needs to be an integer
    updates the title of a specific note
    """
    update_title(title, note_id, db)

@note_app.command()
def update_content(content: list[str], note_id: int):
    """
    :param content: The content of the note, needs to be a string or list of strings, for adding a simple or bookmark note, enter only one 'word' as the content
    :param note_id: The id of the note, needs to be an integer
    updates the content of a specific note
    """
    update_content(content, note_id, db)

@note_app.command()
def update(note_id: int,title: Optional[str] = typer.Option(None, "--title", "-t"), content: Optional[str | list[str]] = typer.Option(None, "--content", "-c")):
    """
    :param note_id: The id of the note, needs to be an integer
    :param title: The title of the given note needs to be a string (an optional parameter)
    :param content: The content of the note, needs to be a string or list of strings, for adding a simple or bookmark note, enter only one 'word' as the content (an optional parameter)
    updates the content and/or the title of a specific note
    """
    update_note(note_id, db, title, content)

if __name__ == "__main__":
    app()