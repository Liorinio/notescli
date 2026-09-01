import logging
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from requests import HTTPError
from notecli.app_types.note_type import NoteType
from notecli.database.database_manager import PostgresDb
from notecli.exceptions.exception_handler import validation_exception_handler
from notecli.memory_storage.db_schema import MemoryStorage
from notecli.services.note_service import retrieve_all_notes, get_note_structure
from notecli.services.note_handlers import add_note, delete_note, view_specific_note, navigate_url, update_note, search_note, get_note
from notecli.utils.restapi_utils import replace_openapi, restapi_middleware, update_request_content_checker, create_request_content_checker, check_note_create_parameters
from notecli.app_types.json_request_models import NoteCreate, NoteUpdate
from notecli.exceptions.not_found_exception import NotFoundError


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
app.exception_handler(RequestValidationError)(validation_exception_handler)


@app.get("/notes/metadata", status_code=200, tags=["Notes"])
def show_metadata():
    output = get_note_structure()
    logger.info("metadata showed")
    return {"metadata": output, "message": "Metadata showed"}


@app.get("/notes", status_code=200, tags=["Notes"])
def list_notes(request: Request,sort_type: str | None = None):
    """Lists notes"""
    database = request.app.state.db

    try:
        note_type = (NoteType[sort_type.upper()] if sort_type is not None else None)

        list_of_notes = retrieve_all_notes(database, note_type)

        if list_of_notes:
            logger.info("Notes listed")
            return {"data": list_of_notes,"message": "Notes are listed"}

        return {"message": "There are no notes because the database is empty"}

    except Exception as error:
        raise HTTPException(status_code=400,detail=str(error))


@app.post("/notes", status_code=201, tags=["Notes"])
def add(request: Request,note: NoteCreate):
    database = request.app.state.db
    content = create_request_content_checker(note)

    try:
        if check_note_create_parameters(note, note.type):
            added_note = add_note(note.type.name,note.title,content,database)
            if added_note:
                logger.info("Note was added")
                return {"message": "Note created successfully", "added note": added_note.to_str()}
            else:
                logger.info("The given requirements didn't allow to create a note of the given type")
                return {"message": "The given requirements didn't allow to create a note of the given type"}
        else:
            logger.info("The given requirements didn't allow to create a note of the given type")
            raise HTTPException(status_code=400, detail="The given requirements didn't allow to create a note of the given type")

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except KeyError as error:
        raise HTTPException(status_code=400,detail=f"Invalid Key {error}")
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))




@app.get("/notes/search", status_code=200, tags=["Notes"], operation_id="searchNotes")
def search(request: Request,title: str | None = None, start_date: datetime | None = None, end_date: datetime | None = None):
    """Searches notes with query parameters"""
    database = request.app.state.db
    try:
        requested_note = search_note(start_date, end_date, title, database)
        if requested_note is None or requested_note == []:
            return {"message": "No notes were found"}
        else:
            return {"note": requested_note, "message": "Notes were found successfully"}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))



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
        if check_note_create_parameters(note_update, note_update.type):
            got_note = get_note(note_id, database)
            if got_note is not None and got_note.note_type.name == note_update.type.name:
                is_updated: bool = update_note(note_id, database, note_update.title, content)
                if is_updated:
                    logger.info("Note was updated")
                    requested_note = view_specific_note(note_id, database)
                    if requested_note is not None:
                        return {"message": "Note updated successfully", "updated note": requested_note}
                else:
                    raise HTTPException(status_code=400, detail="Failed to update note, same fields as before")
            else:
                logger.info("The given requirements didn't allow to create a note of the given type")
                raise HTTPException(status_code=400, detail="The given requirements didn't allow to create a note of the given type, cannot swamp types")
        else:
            logger.info("The given requirements didn't allow to create a note of the given type")
            raise HTTPException(status_code=400, detail="The given requirements didn't allow to create a note of the given type, wrong parameters")
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
            logger.info("Can't open a url for a note without url")
            raise HTTPException(status_code=502, detail="Note doesn't have a url")
        else:
            logger.info("Note's content was shown")
            return {"output": output, "message": "Note's url navigated successfully"}
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except HTTPError as error:
        raise HTTPException(status_code=502, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


if __name__ == "__main__":
    uvicorn.run("restapi:app", host="127.0.0.1", port=8080, reload=True)
