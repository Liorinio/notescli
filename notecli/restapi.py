import logging
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from notecli.database.database_manager import PostgresDb
from notecli.memory_storage.db_schema import MemoryStorage
from notecli.services.note_service import retrieve_all_notes, get_note_structure
from notecli.services.note_handlers import add_note, delete_note, view_specific_note, navigate_url, update_note, search_note
from notecli.utils.restapi_utils import replace_openapi, restapi_middleware, update_request_content_checker, create_request_content_checker
from notecli.app_types.json_request_models import NoteCreate, NoteUpdate
from notecli.exceptions import NotFoundError


db = None
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.db = MemoryStorage()
    application.state.db = application.state.db.parse_from_dict(PostgresDb.load_from_db())
    logger.info("The database has been loaded, layer: restapi")

    yield

    application.state.db = None
    logger.info("The database is shutting down, layer: restapi")


app = FastAPI(lifespan=lifespan)
app.openapi = replace_openapi
app.middleware("http")(restapi_middleware)


@app.get("/notes/metadata", status_code=200, tags=["Notes"])
def show_metadata():
    output = get_note_structure()
    logger.info("metadata showed")
    return {"metadata": output, "message": "Metadata showed"}

@app.get("/notes", status_code=200, tags=["Notes"])
def list_notes(request: Request):
    """Lists notes"""
    database = request.app.state.db
    try:
        list_of_notes = retrieve_all_notes(database)
        if list_of_notes:
            logger.info("Notes listed")
            return {"data": list_of_notes, "message": "Notes are listed"}
        else:
            return {"message": "There are not notes due to none existed database"}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))



@app.post("/notes", status_code=201, tags=["Notes"])
def add(request: Request,note: NoteCreate):
    database = request.app.state.db

    content = create_request_content_checker(note)

    try:
        add_note(note.type.name,note.title,content,database)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except KeyError as error:
        raise HTTPException(status_code=400,detail=f"Invalid Key {error}")
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

    logger.info("Note was added")

    return {"message": "Note created successfully"}


@app.get("/notes/search", status_code=200, tags=["Notes"], operation_id="searchNotes")
def search(request: Request,title: str,start_date: datetime,end_date: datetime):
    """Searches notes with query parameters"""
    database = request.app.state.db
    try:
        requested_note = search_note(start_date, end_date, title, database)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note was found")
    return {"note": requested_note, "message": "Notes were found successfully"}


@app.get("/notes/{note_id}", status_code=200, tags=["Notes"])
def view(note_id: int, request: Request):
    """Gets a specific note, using the note's id for getting it"""
    database = request.app.state.db
    try:
        requested_note = view_specific_note(note_id, database)
        if requested_note is None:
            return {"message": "Note doesn't exist"}
        else:
            logger.info("Note viewed")
            return {"note": requested_note, "message": "Note viewed successfully"}

    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))




@app.put("/notes/{note_id}", status_code=200, tags=["Notes"])
def update(note_id: int, note_update: NoteUpdate, request: Request):
    """Updates a note, using a JSON Request Body"""
    database = request.app.state.db
    content: list[str] | str | None = update_request_content_checker(note_update)

    try:
        is_updated: bool = update_note(note_id, database, note_update.title, content)
        if is_updated:
            logger.info("Note was updated")
            return {"message": "Note updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to update note")
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.delete("/notes/{note_id}", status_code=204, tags=["Notes"])
def delete(note_id: int, request: Request):
    """Deletes a note by ID"""
    database = request.app.state.db
    try:
        delete_note(note_id, database)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except BlockingIOError as error:
        raise HTTPException(status_code=500, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note was deleted")

@app.get("/notes/{note_id}/navigate", status_code=200, tags=["Notes"])
def navigate(note_id: int, request: Request):
    """Fetches the content of a bookmark URL"""
    database = request.app.state.db
    try:
        output = navigate_url(note_id, database)

        if output is None:
            return {"message": "Note doesn't exist"}
        else:
            logger.info("Note's content was shown")
            return {"output": output, "message": "Note's url navigated successfully"}
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


if __name__ == "__main__":
    uvicorn.run("restapi:app", host="127.0.0.1", port=8080, reload=True)
