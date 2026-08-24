import logging
from datetime import datetime
from typing import Optional
import typer
from notecli.memory_storage.db_schema import Db
from notecli.database.FileManager import PostgresDb
from notecli.services.note_service import show_note_structure
from notecli.services.note_handlers import add_note, delete_note, view_specific_note, navigate_url, update_note, search_note, update_content, update_title, get_all_notes

app = typer.Typer()
note_app = typer.Typer()
app.add_typer(note_app, name="note")
db: Db | None = None

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


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
    try:
        print(get_all_notes(db))
    except Exception as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)
    typer.echo("Notes showed successfully")


@note_app.command()
def add(given_note_type: str, title: str, content: list[str]):
    """
    :param given_note_type: The type of the given note (simple/bookmark/list), needs to be a string
    :param title: The title of the given note, needs to be a string
    :param content: The content of the note, needs to be a string or list of strings, for adding a simple or bookmark note, enter only one 'word' as the content
    adds a note to the database
    """
    try:
        add_note(given_note_type, title, content, db)

    except ValueError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)

    except KeyError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=2)

    typer.echo("Note created successfully")


@note_app.command()
def delete(note_id: int):
    """
    :param note_id: The id of the note, needs to be an integer
    deletes a note from the database
    """
    try:
        delete_note(note_id, db)
    except ValueError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)
    except BlockingIOError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=2)

    typer.echo("Note deleted successfully")


@note_app.command()
def show_structure():
    """
    shows the structure of the notes that are available for usage in the system
    """
    print(show_note_structure())
    typer.echo("Metadata showed successfully")


@note_app.command()
def search(early_creation_date: datetime, late_creation_date: datetime, title: str):
    """
    :param title: The title of the note, needs to be a string type
    :param early_creation_date: The date which the note was created. needs to be a datetime type
    :param late_creation_date: The date which the note was updated. needs to be a datetime type
    searches and prints a specific note
    """
    try:
        print(search_note(early_creation_date, late_creation_date, title, db))
    except Exception as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Notes were found successfully")


@note_app.command(name="view")
def view_note(note_id: int):
    """
    :param note_id: The id of the note, needs to be an integer
    shows a specific note
    """
    try:
        print(view_specific_note(note_id, db))
    except Exception as Error:
        typer.echo(f"Error: {Error}", err=True)
        raise typer.Exit(code=1)
    typer.echo("Note's content viewed successfully")


@note_app.command()
def navigate(note_id: int):
    """
    :param note_id: The id of the note, needs to be an integer
    shows the content of the url, if the note is a BookMarkNote
    """
    try:
        print(navigate_url(note_id, db))
    except ValueError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1)
    typer.echo("Note's url navigated successfully")


@note_app.command()
def update_title(title: str, note_id: int):
    """
    :param title: The title of the given note, needs to be a string
    :param note_id: The id of the note, needs to be an integer
    updates the title of a specific note
    """
    try:
        if isinstance(title, str):
            res = update_title(title, note_id, db)
            if not res:
                raise typer.Exit(code=1)
        else:
            raise typer.Exit(code=2)
    except ValueError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=3)
    typer.echo("Note's title updated successfully")


@note_app.command()
def update_content(content: list[str], note_id: int):
    """
    :param content: The content of the note, needs to be a string or list of strings, for adding a simple or bookmark note, enter only one 'word' as the content
    :param note_id: The id of the note, needs to be an integer
    updates the content of a specific note
    """
    try:
        if isinstance(content, str) or isinstance(content, list):
            res = update_content(content, note_id, db)
            if not res:
                raise typer.Exit(code=1)
        else:
            raise typer.Exit(code=2)
    except Exception as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=3)
    typer.echo("Note's content updated successfully")


@note_app.command()
def update(note_id: int, title: Optional[str] = typer.Option(None, "--title", "-t"),
           content: Optional[list[str]] = typer.Option(None, "--content", "-c")):
    """
    :param note_id: The id of the note, needs to be an integer
    :param title: The title of the given note needs to be a string (an optional parameter)
    :param content: The content of the note, needs to be a string or list of strings, for adding a simple or bookmark note, enter only one 'word' as the content (an optional parameter)
    updates the content and/or the title of a specific note
    """
    try:
        res = update_note(note_id, db, title, content)
        if not res:
            raise typer.Exit(code=1)
    except ValueError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=2)
    typer.echo(f"Note number {note_id} was updated successfully")


if __name__ == "__main__":
    app()
