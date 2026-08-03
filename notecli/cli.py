import logging
import typer
from notecli.app_types.NoteType import NoteType
from notecli.db_schema import Db
from notecli.notecli_commands import adder, print_all
from notecli.FileManager import DbFileStorage

app = typer.Typer()
note_app = typer.Typer()
app.add_typer(note_app, name="note")
db: Db | None = None

logging.basicConfig(level = logging.INFO, format='%(levelname)s: %(message)s')

@app.callback()
def main():
    global db
    db = Db.parse_from_dict(DbFileStorage.load_from_json("db2.json"))

@note_app.command(name="list")
def list_notes():
    print_all(db)

@note_app.command()
def add(given_note_type: str, title: str, content: str):
    if db is not None:
        note_type: NoteType = NoteType[given_note_type]
        adder(note_type, title, content, db)
        DbFileStorage.save_to_db(db.parse_to_dict(), "db2.json")


if __name__ == "__main__":
    app()