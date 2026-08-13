import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from notecli.database.FileManager import PostgresDb
from notecli.memory_storage.db_schema import Db
from notecli.services.notes_commands import add_note, delete_note, view_note, navigate_url, update_note, search_note, update_content, update_title, show_notes_structure, print_all_notes

db = None
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.db = Db()
    application.state.db = application.state.db.parse_from_dict(PostgresDb.load_from_db())

    yield

    application.state.db = None


app = FastAPI(lifespan=lifespan)

logging.basicConfig(level = logging.INFO, format='%(levelname)s: %(message)s')


@app.get("/notes")
def show_metadata():
    show_notes_structure()
    raise HTTPException(status_code=200, detail="metadata showed")

@app.post("/notes")
def add(given_note_type: str, title: str, content: list[str]):
    add_note(given_note_type, title,content, db)

@app.delete("/notes/{id}")
def delete(note_id: int):
    delete_note(note_id, db)

@app.get("/notes/sreach")
def search(note_id: int, start_date: datetime, end_date: datetime):
    search_note(start_date, end_date, note_id, db)

@app.post("/notes/{id}")
def update(note_id: int, title:Optional[str], content: Optional[str | list[str]]):
    update_note(note_id, db, title, content)

@app.post("/notes/{id}/title")
def update_note_title(note_id: int, title:Optional[str]):
    if isinstance(title, str):
        update_title(title, note_id, db)
        raise HTTPException(status_code=200)
    else:
        raise HTTPException(status_code=400)

@app.post("/notes/{id}/content")
def update_note_content(note_id: int, content: Optional[str | list[str]]):
    if isinstance(content, str) or isinstance(content, list):
        update_content(content, note_id, db)
        raise HTTPException(status_code=200)
    else:
        raise HTTPException(status_code=400)

@app.get("/notes/{id}/navigate")
def navigate(note_id: int):
    navigate_url(note_id, db)

@app.get("/notes/{id}")
def view(note_id: int):
    view_note(note_id, db)

@app.get("/notes")
def list_notes():
    print_all_notes(db)
