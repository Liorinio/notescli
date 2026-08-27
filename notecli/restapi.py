import logging
from contextlib import asynccontextmanager
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, Request, Query, Path, Body
from notecli.database.DbManager import PostgresDb
from notecli.memory_storage.db_schema import MemoryStorage
from notecli.app_types.models_place_holder import NoteCreateRequest, NotePlaceHolder, NotePage, BookmarkNoteUpdateRequest, SimpleNoteUpdateRequest, ListNoteUpdateRequest
from notecli.services.note_service import retrieve_all_notes, get_note_structure
from notecli.services.note_handlers import add_note, delete_note, view_specific_note, navigate_url, update_note, search_note, update_content, update_title
import uvicorn
import yaml

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


with open("C:\\Users\\FirstUser\\PycharmProjects\\notescli\\notebookOpenAPI.yaml","r") as file:
    custom_openapi_schema = yaml.safe_load(file)

original_openapi = app.openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    generated_schema = original_openapi()
    generated_schema["info"] = custom_openapi_schema.get("info",generated_schema["info"])
    generated_schema["paths"].update(custom_openapi_schema.get("paths", {}))

    app.openapi_schema = generated_schema
    return app.openapi_schema


app.openapi = custom_openapi

@app.get("/notes/metadata", status_code=200, tags=["view"])
def show_metadata():
    output = get_note_structure()
    logger.info("metadata showed")
    return {"metadata": output ,"message": "Metadata showed"}


@app.post("/notes/add and remove", status_code=201, tags=["add and remove"])
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


@app.get("/notes/search", status_code=200,tags=["Notes"], operation_id="searchNotes")
def search(request: Request, title: str, start_date: datetime, end_date: datetime):
    database = request.app.state.db
    try:
        requested_note = search_note(start_date, end_date, title, database)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Note was found")
    return {"note": requested_note, "message": f"Notes were found successfully"}


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


@app.get("/view/notes", status_code=200, tags=["view"])
def list_notes(request: Request):
    database = request.app.state.db
    try:
        list_of_notes = retrieve_all_notes(database)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    logger.info("Notes listed")
    return {"data": list_of_notes, "message": "Notes are listed"}

"--------------------------------------"
#Not implemented functions (function that are in the openapi, but I didn't require to implement)
#The only reason they are here is to have them on the swagger, they don't do anything


@app.get("/notes",status_code=200,tags=["Notes"],operation_id="listNotes",summary="List notes (metadata only)",description=(
        "Returns a paginated list of note metadata — id, type, title, ""createdAt, updatedAt. Content fields (text, list, url) are omitted. ""Equivalent to `nb note list`."))
def list_notes(type: str | None = Query(None, description="Filter by note type")):
    raise HTTPException(status_code=501,detail="Not implemented")

@app.post(
    "/notes",
    status_code=201,
    operation_id="createNote",
    summary="Create a new note",
    description=(
        "Creates a new note. The `type` field acts as a discriminator — "
        "send `simple`, `list`, or `bookmark` and include the matching "
        "content field (`text`, `list`, or `url`). "
        "Equivalent to `nb note create simple|list|bookmark`."
    ),
    tags=["Notes"],
    response_model=NotePlaceHolder
)
def create_note(note: NoteCreateRequest,request: Request):
    raise HTTPException(status_code=501,detail="Not implemented")

@app.delete(
    "/notes",
    operation_id="deleteNotesByDate",
    summary="Delete all notes created on a specific date",
    description="Bulk-deletes every note whose createdAt date matches the given date.",
    tags=["Notes"]
)
def delete_notes_by_date(date: date):
    raise HTTPException(status_code=501, detail="Not implemented")


@app.get(
    "/notes/search",
    operation_id="searchNotes",
    summary="Search notes",
    description="Full-content search with optional filters.",
    tags=["Notes"],
    response_model=NotePage
)
def search_notes(
    title: str | None = Query(None, min_length=1),
    dateFrom: date | None = None,
    dateTo: date | None = None,
    tags: list[str] | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    raise HTTPException(status_code=501, detail="Not implemented")


@app.get(
    "/notes/{id}",
    operation_id="getNote",
    summary="Get a specific note",
    description="Returns the full note including content fields.",
    tags=["Notes"],
    response_model=NotePlaceHolder
)
def get_note(id: int = Path(..., ge=1)):
    raise HTTPException(status_code=501, detail="Not implemented")


@app.put(
    "/notes/{id}",
    operation_id="updateNote",
    summary="Update a note",
    tags=["Notes"],
    response_model=NotePlaceHolder
)
def update_note(id: int = Path(..., ge=1),note: (SimpleNoteUpdateRequest| ListNoteUpdateRequest| BookmarkNoteUpdateRequest) = Body(...)):
    raise HTTPException(status_code=501,detail="Not implemented")


@app.delete(
    "/notes/{id}",
    status_code=204,
    operation_id="deleteNote",
    summary="Delete a note by ID",
    description="Equivalent to `nb note delete [id]`.",
    tags=["Notes"]
)
def delete_note(id: int = Path(..., ge=1)):
    raise HTTPException(status_code=501, detail="Not implemented")


@app.patch(
    "/notes/{id}/tags",
    operation_id="updateNoteTags",
    summary="Replace tags on a note",
    description="Replaces the tag list on the note with the supplied array.",
    tags=["Notes"],
    response_model=NotePlaceHolder
)
def update_note_tags(id: int = Path(..., ge=1),note: (SimpleNoteUpdateRequest| ListNoteUpdateRequest| BookmarkNoteUpdateRequest) = Body(...)):
    raise HTTPException(status_code=501, detail="Not implemented")


@app.get(
    "/notes/{id}/navigate",
    operation_id="navigateNote",
    summary="Fetch the content of a bookmark URL",
    description="Returns the content of the URL stored in a bookmark note.",
    tags=["Notes"]
)
def navigate_note(id: int = Path(..., ge=1)):
    raise HTTPException(status_code=501, detail="Not implemented")


if __name__ == "__main__":
    uvicorn.run("restapi:app", host="127.0.0.1", port=8080, reload=True)
