import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from notecli.app_types.NoteType import NoteType
from notecli.database.DbManager import PostgresDb
from notecli.memory_storage.db_schema import MemoryStorage
from notecli.services.note_service import retrieve_all_notes, get_note_structure
from notecli.services.note_handlers import add_note, delete_note, view_specific_note, navigate_url, update_note, search_note
import uvicorn
import yaml
import os
from dotenv import load_dotenv


db = None
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.db = MemoryStorage()
    application.state.db = application.state.db.parse_from_dict(PostgresDb.load_from_db())

    yield

    application.state.db = None


app = FastAPI(lifespan=lifespan)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


load_dotenv()

with open(os.environ["OPENAPI_FILE_PATH"],"r", encoding="utf-8") as file:
    custom_openapi_schema = yaml.safe_load(file)

original_openapi = app.openapi

def custom_openapi():
    return custom_openapi_schema


app.openapi = custom_openapi

from pydantic import BaseModel, HttpUrl, field_validator
from typing import List, Optional


# ─── Pydantic Models for JSON Request Bodies ──────────────────────────────
class NoteCreate(BaseModel):
    type: NoteType
    title: str
    text: Optional[str] = None
    list: Optional[List[str]] = None
    url: Optional[HttpUrl] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": 1,
                    "title": "My First Note",
                    "text": "Hello world!"
                }
            ]
        }
    }

    @field_validator("type", mode="before")
    @classmethod
    def parse_string_to_enum(cls, value):
        if isinstance(value, str):
            mapping = {"simple": 1, "listnote": 2, "bookmark": 3}
            val_lower = value.lower()
            if val_lower in mapping:
                return mapping[val_lower]
            raise ValueError("Type must be 'simple', 'listnote', or 'bookmark'")
        return value


class NoteUpdate(BaseModel):
    type: NoteType
    title: Optional[str] = None
    text: Optional[str] = None
    list: Optional[List[str]] = None
    url: Optional[HttpUrl] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "My First Note",
                    "text": "Hello world!",
                    "list": ["hello", "world!"],
                    "url": "https://fastapi.tiangolo.com"
                }
            ]
        }
    }

    @field_validator("type", mode="before")
    @classmethod
    def parse_string_to_enum(cls, value):
        if isinstance(value, str):
            mapping = {"simple": 1, "listnote": 2, "bookmark": 3}
            val_lower = value.lower()
            if val_lower in mapping:
                return mapping[val_lower]
            raise ValueError("Type must be 'simple', 'listnote', or 'bookmark'")
        return value


# ─── Endpoints ────────────────────────────────────────────────────────────

@app.get("/notes/metadata", status_code=200, tags=["Notes"])
def show_metadata():
    output = get_note_structure()
    logger.info("metadata showed")
    return {"metadata": output, "message": "Metadata showed"}

@app.get("/notes", status_code=200, tags=["Notes"])
def list_notes(request: Request):
    """List notes (metadata only)"""
    database = request.app.state.db
    try:
        list_of_notes = retrieve_all_notes(database)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Notes listed")
    return {"data": list_of_notes, "message": "Notes are listed"}



@app.post("/notes", status_code=201, tags=["Notes"])
def add(note: NoteCreate, request: Request):
    """Create a new note using a JSON Request Body"""
    database = request.app.state.db
    content: list[str] | None = None

    if note.text is not None:
        content = [note.text]
    elif note.list is not None:
        content = note.list
    elif note.url is not None:
        content = [str(note.url)]

    try:
        add_note(note.type.name, note.title, content, database)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except KeyError as error:
        raise HTTPException(status_code=400, detail=f'Invalid Key {error}')
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

    logger.info("Note was added")
    return {"message": "Note created successfully"}


@app.get("/notes/search", status_code=200, tags=["Notes"], operation_id="searchNotes")
def search(request: Request,title: str,start_date: datetime,end_date: datetime):
    """Search notes with optional query parameters"""
    database = request.app.state.db
    try:
        requested_note = search_note(start_date, end_date, title, database)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note was found")
    return {"note": requested_note, "message": "Notes were found successfully"}

@app.get("/notes/{note_id}", status_code=200, tags=["Notes"])
def view(note_id: int, request: Request):
    """Get a specific note"""
    database = request.app.state.db
    try:
        requested_note = view_specific_note(note_id, database)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note viewed")
    return {"note": requested_note, "message": "Note viewed successfully"}


@app.put("/notes/{note_id}", status_code=200, tags=["Notes"])
def update(note_id: int, note_update: NoteUpdate, request: Request):
    """Update a note using a JSON Request Body"""
    database = request.app.state.db
    content: list[str] | str | None = None

    if note_update.text is not None:
        content = note_update.text
    elif note_update.list is not None:
        content = note_update.list
    elif note_update.url is not None:
        content = str(note_update.url)

    try:
        res = update_note(note_id, database, note_update.title, content)
        if not res:
            raise HTTPException(status_code=400, detail="Failed to update note")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

    logger.info("Note was updated")
    return {"message": "Note updated successfully"}

@app.delete("/notes/{note_id}", status_code=204, tags=["Notes"])
def delete(note_id: int, request: Request):
    """Delete a note by ID"""
    database = request.app.state.db
    try:
        delete_note(note_id, database)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except BlockingIOError as error:
        raise HTTPException(status_code=500, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note was deleted")

@app.get("/notes/{note_id}/navigate", status_code=200, tags=["Notes"])
def navigate(note_id: int, request: Request):
    """Fetch the content of a bookmark URL"""
    database = request.app.state.db
    try:
        output = navigate_url(note_id, database)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note's content was shown")
    return {"output": output, "message": "Note's url navigated successfully"}

if __name__ == "__main__":
    uvicorn.run("restapi:app", host="127.0.0.1", port=8080, reload=True)
