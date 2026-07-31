import logging
import typer
from app_types.NoteType import NoteType
from notecli_commands import adder, print_all

app = typer.Typer()
note_app = typer.Typer()
app.add_typer(note_app, name="note")

logging.basicConfig(level = logging.INFO, format='%(levelname)s: %(message)s')

@note_app.command()
def add(given_note_type: str,title: str,content: str):
    note_type: NoteType = NoteType[given_note_type]
    adder(note_type, title, content, "db2.json")

@note_app.command(name="list")
def list_notes():
    print_all()

if __name__ == "__main__":
    app()