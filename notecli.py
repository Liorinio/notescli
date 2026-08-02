import logging
import typer

from NoteDict import NoteDict
from app_types.NoteType import NoteType
from db_schema import Db
from notecli_commands import adder, print_all
from FileManager import DbFileStorage

app = typer.Typer()
note_app = typer.Typer()
app.add_typer(note_app, name="note")
db: Db | None = None

logging.basicConfig(level = logging.INFO, format='%(levelname)s: %(message)s')

@app.callback()
def main():
    global db
    if db is None:
        #db = Db.load_from_json("db2.json")

        nt: NoteDict = DbFileStorage.load_from_json("db2.json")
        db = Db.parse_from_dict(nt)


@note_app.command(name="list")
def list_notes():
    if db is not None:
        print_all(db)

@note_app.command()
def add(given_note_type: str, title: str, content: str):
    if db is not None:
        note_type: NoteType = NoteType[given_note_type]
        adder(note_type, title, content, db)
        #db.save_to_json("db2.json")
        DbFileStorage.save_to_db(db, "db2.json")


if __name__ == "__main__":
    app()