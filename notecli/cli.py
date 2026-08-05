import logging
from datetime import datetime
from platform import node

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
    db = db.parse_from_dict(DbFileStorage.load_from_json("db2.json"))

@note_app.command(name="list")
def list_notes():
    print_all(db)

@note_app.command()
def add(given_note_type: str, title: str, content: str):
    if db is not None:
        note_type: NoteType = NoteType[given_note_type]
        adder(note_type, title, content, db)
        DbFileStorage.save_to_db(db.parse_to_dict(), "db2.json")

@note_app.command()
def delete(note_id: int):
    if db is not None:
        delete_note(note_id, db)
        DbFileStorage.save_to_db(db.parse_to_dict(), "db2.json")

@note_app.command()
def show_structure():
    show_note_structure()

@note_app.command()
def search(early_creation_date: datetime, late_creation_date: datetime,note_id: int):
    if db is not None:
        returned_note = search_note_by_date_and_id(early_creation_date,late_creation_date, db, note_id)
        if returned_note is not None:
            print(returned_note)
        else:
            print("None")


@note_app.command(name="view")
def view_note(note_id: int):
    if db is not None:
        returned_description = search_note_by_id(note_id, db)
        if returned_description is not None:
            print(returned_description)
        else:
            print("None")

@note_app.command()
def navigate(note_id: int):
    if db is not None:
        returned_output = show_content_url(note_id, db)
        if returned_output is not None:
            print(returned_output[0])
            print(returned_output[1])
        else:
            print("None")

@note_app.command()
def update_title(title: str, note_id: int):
    if db is not None:
        update_note_title(title, note_id, db)
        DbFileStorage.save_to_db(db.parse_to_dict(), "db2.json")

@note_app.command()
def update_content(title: str, note_id: int):
    if db is not None:
        update_note_content(title, note_id, db)
        DbFileStorage.save_to_db(db.parse_to_dict(), "db2.json")


if __name__ == "__main__":
    app()