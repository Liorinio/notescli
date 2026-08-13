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


@app.get("/notes", status_code=200)
def show_metadata():
    show_notes_structure()
    return {"message": "Metadata showed"}

@app.post("/notes", status_code=201)
def add(given_note_type: str, title: str, content: list[str]):
    try:
        add_note(given_note_type, title,content, db)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except KeyError as error:
        raise HTTPException(status_code=404, detail=f'Invalid Key {error}')
    return {"message": "Note created successfully"}

@app.delete("/notes/{id}", status_code=200)
def delete(note_id: int):
    try:
        delete_note(note_id, db)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"message": "note deleted successfully"}

@app.get("/notes/sreach", status_code=200)
def search(note_id: int, start_date: datetime, end_date: datetime):
    search_note(start_date, end_date, note_id, db)

@app.post("/notes/{id}", status_code=200)
def update(note_id: int, title:Optional[str], content: Optional[str | list[str]]):
    update_note(note_id, db, title, content)

@app.post("/notes/{id}/title", status_code=200)
def update_note_title(note_id: int, title:Optional[str]):
    if isinstance(title, str):
        update_title(title, note_id, db)
        raise HTTPException(status_code=200)
    else:
        raise HTTPException(status_code=400)

@app.post("/notes/{id}/content", status_code=200)
def update_note_content(note_id: int, content: Optional[str | list[str]]):
    if isinstance(content, str) or isinstance(content, list):
        update_content(content, note_id, db)
        raise HTTPException(status_code=200)
    else:
        raise HTTPException(status_code=400)

@app.get("/notes/{id}/navigate", status_code=200)
def navigate(note_id: int):
    navigate_url(note_id, db)

@app.get("/notes/{id}", status_code=200)
def view(note_id: int):
    view_note(note_id, db)

@app.get("/notes", status_code=200)
def list_notes():
    print_all_notes(db)
