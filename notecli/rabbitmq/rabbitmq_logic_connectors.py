import logging
from notecli.app_types.note_models import NoteSimple, NoteBookMark, NoteList
from notecli.app_types.note_type import NoteType
from notecli.app_types.rabbitmq_validation_models import NavigateNoteParams, AddNoteParams, DeleteNoteParams, \
    GetAllNotesParams, SearchNoteParams, ViewNoteParams, UpdateNoteParams
from notecli.exceptions.not_found_exception import NotFoundError
from notecli.memory_storage.db_schema import MemoryStorage
from notecli.services.note_handlers import add_note, delete_note, view_specific_note, navigate_url, update_note, \
    search_note, get_note
from notecli.services.note_service import retrieve_all_notes, get_note_structure
from notecli.utils.rabbitmq_utils import request_content_checker_rabbit_update, \
    check_note_create_parameters_rabbit_update

logger = logging.getLogger(__name__)


def add_connector(add_params: AddNoteParams, db: MemoryStorage | None):
    try:
        added_note: NoteSimple | NoteBookMark | NoteList | None = add_note(add_params['given_note_type'],
                                                                           add_params['title'], add_params['content'],
                                                                           db)

        if not added_note:
            logger.info("The given requirements didn't allow to create a note of the given type")
            return {"message": "The given requirements didn't allow to create a note of the given type"}
        else:
            logger.info("Note was added")
            return {"message": "Note created successfully", "added note": added_note.to_str()}
    except ValueError as error:
        return {"message": "The given requirements didn't allow to create a note of the given type",
                "error": str(error)}
    except KeyError as error:
        return {"message": "The given requirements didn't allow to create a note of the given type",
                "error": str(error)}
    except Exception as error:
        return {"message": "The given requirements didn't allow to create a note of the given type",
                "error": str(error)}


def delete_connector(delete_params: DeleteNoteParams, db: MemoryStorage | None):
    try:
        delete_note(delete_params["note_id"], db)
        logger.info("Note was deleted")
        return {"message": f"Note {delete_params['note_id']} successfully deleted."}
    except NotFoundError as error:
        return {"message": "The given requirements didn't allow to delete the note of the given type",
                "error": str(error)}
    except BlockingIOError as error:
        return {
            "message": "The given requirements didn't allow to delete the note of the given type, IO operation blocked",
            "error": str(error)}
    except Exception as error:
        return {"message": "The given requirements didn't allow to delete the note of the given type, unknown error",
                "error": str(error)}


def navigate_connector(navigate_params: NavigateNoteParams, db: MemoryStorage | None):
    try:
        output = navigate_url(navigate_params["note_id"], db)

        if output is None:
            logger.info("Can't open a url for a note without url")
            return {"message": "Can't open a url for a note without url"}
        else:
            logger.info("Note's content was shown")
            return {"output": output, "message": "Note's url navigated successfully"}
    except NotFoundError as error:
        return {"message": "The given requirements didn't allow to open the note's url", "error": str(error)}
    except Exception as error:
        return {"message": "The given requirements didn't allow to open the note's url", "error": str(error)}


def get_all_notes_connector(get_notes_params: GetAllNotesParams, db: MemoryStorage | None):
    try:
        sort_type = get_notes_params["sort_type"]
        note_type = NoteType[sort_type.upper()] if sort_type is not None else None
        list_of_notes = retrieve_all_notes(db, note_type)

        if list_of_notes:
            logger.info("Notes listed")
            return {"data": list_of_notes, "message": "Notes are listed"}

        return {"message": "There are no notes because the database is empty"}

    except Exception as error:
        return {"message": "Cannot retrieve notes due to an error", "error": str(error)}


def search_connector(search_params: SearchNoteParams, db: MemoryStorage | None):
    try:
        requested_note = search_note(search_params['early_creation_date'], search_params['late_creation_date'],
                                     search_params['title'], db)
        if requested_note is None or requested_note == []:
            raise NotFoundError("No notes were found")
        else:
            return {"note": requested_note, "message": "Notes were found successfully"}
    except NotFoundError as error:
        return {"message": "No notes were found due to an error", "error": str(error)}
    except Exception as error:
        return {"message": "No notes were found due to an error", "error": str(error)}


def view_connector(view_params: ViewNoteParams, db: MemoryStorage | None):
    try:
        requested_note = view_specific_note(view_params['note_id'], db)
        if requested_note is None:
            return {"message": "Note doesn't exist"}
        else:
            logger.info("Note viewed")
            return {"note": requested_note, "message": "Note viewed successfully"}

    except NotFoundError as error:
        return {"message": "No note was viewed due to an error", "error": str(error)}
    except Exception as error:
        return {"message": "No note was viewed due to an error", "error": error}


def update_connector(update_params: UpdateNoteParams, db: MemoryStorage | None):
    content: list[str] | str | None = request_content_checker_rabbit_update(update_params)

    try:
        if db is not None:
            existing_note = db.get_note_from_db_by_id(update_params["note_id"])

            if not check_note_create_parameters_rabbit_update(update_params, existing_note.note_type):
                return {
                    "status": "error","message": "The given requirements didn't allow to update a note of the given type, wrong parameters"
                }

            got_note = get_note(update_params["note_id"], db)
            incoming_type = update_params.get("note_type")

            if got_note is None:
                return {"message": f"Note not found"}

            if incoming_type is not None and NoteType(incoming_type) != existing_note.note_type:
                return {"message": "Cannot change the note type"}

            '''
            if got_note.note_type != update_params["note_id"]:
                return {"message": "Cannot change the note type"}
            '''
            is_updated = update_note(update_params["note_id"], db, update_params["title"], content)
            if not is_updated:
                raise {"message": "Failed to update note, same fields as before"}

            requested_note = view_specific_note(update_params["note_id"], db)
            if requested_note is None:
                return {"message": f"Note {update_params["note_id"]} not found after update"}

            logger.info("Note was updated")
            return {"message": "Note updated successfully", "updated note": requested_note}

    except NotFoundError as error:
        return {"message": str(error)}

    except Exception as error:
        logger.exception("Unexpected error while updating note")
        raise {"message": f"Internal server error, {str(error)}"}


def metadata_connector():
    output = get_note_structure()
    logger.info("metadata showed")
    return {"metadata": output, "message": "Metadata showed"}
