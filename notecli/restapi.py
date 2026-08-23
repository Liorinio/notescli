import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from notecli.database.FileManager import PostgresDb
from notecli.memory_storage.db_schema import Db
from notecli.services.note_service import retrieve_all_notes, get_note_structure
from notecli.services.note_handlers import add_note, delete_note, view_specific_note, navigate_url, update_note, search_note, update_content, update_title
import uvicorn

db = None
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.db = Db()
    application.state.db = application.state.db.parse_from_dict(PostgresDb.load_from_db())

    yield

    application.state.db = None


app = FastAPI(lifespan=lifespan)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


@app.get("/notes/metadata", status_code=200, tags=["view"])
def show_metadata():
    output = get_note_structure()
    logger.info("metadata showed")
    return {"metadata": output ,"message": "Metadata showed"}


@app.post("/notes", status_code=201, tags=["add and remove"])
def add(given_note_type: str, title: str, content: list[str], request: Request):
    database = request.app.state.db
    try:
        add_note(given_note_type, title, content, database)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except KeyError as error:
        raise HTTPException(status_code=400, detail=f'Invalid Key {error}')
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note was added")
    return {"message": "Note created successfully"}


@app.delete("/notes/{note_id}", status_code=204, tags=["add and remove/note id usage"])
def delete(note_id: int, request: Request):
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
    return {"message": f"Note number {note_id} was deleted successfully"}


@app.get("/notes/sreach", status_code=200,tags=["view"])
def search(note_id: int, start_date: datetime, end_date: datetime, request: Request):
    database = request.app.state.db
    try:
        requested_note = search_note(start_date, end_date, note_id, database)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note was found")
    return {"note": requested_note, "message": f"Note number {note_id} was found successfully"}


@app.put("/notes/{note_id}", status_code=200,  tags=["note id usage/update"])
def update(note_id: int,request: Request, title: str | None = None, content: str | list[str] | None = None):
    database = request.app.state.db

    try:
        res = update_note(note_id, database, title, content)
        if not res:
            raise HTTPException(status_code=400)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note was updated")
    return {"message": "Note updated successfully"}


@app.put("/notes/{note_id}/title", status_code=200, tags=["note id usage/update"])
def update_note_title(note_id: int, request: Request, title: str | None = None):
    database = request.app.state.db
    try:
        if isinstance(title, str):
            res = update_title(title, note_id, database)
            if not res:
                raise HTTPException(status_code=400)
        else:
            raise HTTPException(status_code=400)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note's title was updated")
    return {"message": "Note's title updated successfully"}


@app.put("/notes/{id}/content", status_code=200, tags=["note id usage/update"])
def update_note_content(note_id: int, request: Request,  content: str | list[str] | None = None):
    database = request.app.state.db
    try:
        if isinstance(content, str) or isinstance(content, list):
            res = update_content(content, note_id, database)
            if not res:
                raise HTTPException(status_code=400)
        else:
            raise HTTPException(status_code=400)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note's content was updated")
    return {"message": "Note's content updated successfully"}


@app.get("/notes/{note_id}/navigate", status_code=200, tags=["note id usage"])
def navigate(note_id: int, request: Request):
    database = request.app.state.db
    try:
        output = navigate_url(note_id, database)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note's content was shown")
    return {"output": output,"message": "Note's url navigated successfully"}


@app.get("/notes/{note_id}", status_code=200, tags=["view/note id usage"])
def view(note_id: int, request: Request):
    database = request.app.state.db
    try:
        requested_note = view_specific_note(note_id, database)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note viewed")
    return {"note": requested_note, "message": "Note's viewed successfully"}


@app.get("/notes", status_code=200, tags=["view"])
def list_notes(request: Request):
    database = request.app.state.db
    try:
        list_of_notes = retrieve_all_notes(database)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Notes listed")
    return {"data": list_of_notes, "message": "Notes are listed"}


if __name__ == "__main__":
    uvicorn.run("restapi:app", host="127.0.0.1", port=8080, reload=True)
