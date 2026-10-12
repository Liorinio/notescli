import logging
from notecli.app_types.note_models import NoteSimple, NoteBookMark, NoteList
from notecli.app_types.note_type import NoteType
from notecli.app_types.rabbitmq_validation_models import NavigateNoteParams, AddNoteParams, DeleteNoteParams, GetAllNotesParams, SearchNoteParams, ViewNoteParams, UpdateNoteParams
from notecli.exceptions.not_found_exception import NotFoundError
from notecli.services.note_handlers import add_note, delete_note, view_specific_note, navigate_url, update_note, search_note, get_note
from notecli.services.note_service import retrieve_all_notes, get_note_structure
from notecli.utils.rabbitmq_utils import request_content_checker_rabbit_update
from notecli.utils.update_parameters_checker import check_note_create_parameters

logger = logging.getLogger(__name__)

def add_connector(add_params: AddNoteParams):
    try:
        added_note: NoteSimple | NoteBookMark | NoteList | None = add_note(add_params['given_note_type'], add_params['title'], add_params['content'], add_params['db'])

        if not added_note:
            logger.info("The given requirements didn't allow to create a note of the given type")
            return {"message": "The given requirements didn't allow to create a note of the given type"}
        else:
            logger.info("Note was added")
            return {"message": "Note created successfully", "added note": added_note.to_str()}
    except ValueError as error:
        return {"message": "The given requirements didn't allow to create a note of the given type", "error": error}
    except KeyError as error:
        return {"message": "The given requirements didn't allow to create a note of the given type", "error": error}
    except Exception as error:
        return {"message": "The given requirements didn't allow to create a note of the given type", "error": error}

def delete_connector(delete_params: DeleteNoteParams):
    try:
        delete_note(delete_params["note_id"], delete_params['db'])
    except NotFoundError as error:
        return {"message": "The given requirements didn't allow to delete the note of the given type", "error": error}
    except BlockingIOError as error:
        return {"message": "The given requirements didn't allow to delete the note of the given type", "error": error}
    except Exception as error:
        return {"message": "The given requirements didn't allow to delete the note of the given type", "error": error}
    logger.info("Note was deleted")
    return None


def navigate_connector(navigate_params: NavigateNoteParams):
    try:
        output = navigate_url(navigate_params["note_id"], navigate_params['db'])

        if output is None:
            logger.info("Can't open a url for a note without url")
            return {"message": "Can't open a url for a note without url"}
        else:
            logger.info("Note's content was shown")
            return {"output": output, "message": "Note's url navigated successfully"}
    except NotFoundError as error:
        return {"message": "The given requirements didn't allow to open the note's url", "error": error}
    except Exception as error:
        return {"message": "The given requirements didn't allow to open the note's url", "error": error}


def get_all_notes_connector(get_notes_params: GetAllNotesParams):
    try:
        sort_type = get_notes_params["sort_type"]
        note_type = NoteType[sort_type.upper()] if sort_type is not None else None
        list_of_notes = retrieve_all_notes(get_notes_params['db'], note_type)

        if list_of_notes:
            logger.info("Notes listed")
            return {"data": list_of_notes, "message": "Notes are listed"}

        return {"message": "There are no notes because the database is empty"}

    except Exception as error:
        return {"message": "Cannot retrieve notes due to an error", "error": error}


def search_connector(search_params: SearchNoteParams):
    try:
        requested_note = search_note(search_params['early_creation_date'], search_params['late_creation_date'], search_params['title'], search_params['db'])
        if requested_note is None or requested_note == []:
            raise NotFoundError("No notes were found")
        else:
            return {"note": requested_note, "message": "Notes were found successfully"}
    except NotFoundError as error:
        return {"message": "No notes were found due to an error", "error": error}
    except Exception as error:
        return {"message": "No notes were found due to an error", "error": error}

def view_connector(view_params: ViewNoteParams):
    try:
        requested_note = view_specific_note(view_params['note_id'], view_params['db'])
        if requested_note is None:
            return {"message": "Note doesn't exist"}
        else:
            logger.info("Note viewed")
            return {"note": requested_note, "message": "Note viewed successfully"}

    except NotFoundError as error:
        return {"message": "No note was viewed due to an error", "error": error}
    except Exception as error:
        return {"message": "No note was viewed due to an error", "error": error}

def update_connector(update_params: UpdateNoteParams):
    content: list[str] | str | None = request_content_checker_rabbit_update(update_params) #create similar func for update params

    try:
        if not check_note_create_parameters(update_params, update_params["note_type"]):  #create similar func for update_params
            return {"message": "The given requirements didn't allow to update a note of the given type, wrong parameters"}

        got_note = get_note(update_params["note_id"], update_params['db'])

        if got_note is None:
            return {"message": f"Note not found"}
        if got_note.note_type != update_params["note_id"]:
            return {"message": "Cannot change the note type"}

        is_updated = update_note(update_params["note_id"], update_params["db"], update_params["title"], content)
        if not is_updated:
            raise {"message": "Failed to update note, same fields as before"}

        requested_note = view_specific_note(update_params["note_id"], update_params["db"])
        if requested_note is None:
            return {"message": f"Note {update_params["note_id"]} not found after update"}

        logger.info("Note was updated")
        return {"message": "Note updated successfully", "updated note": requested_note}

    except NotFoundError as error:
        return {"message": str(error)}

    except Exception as error:
        logger.exception("Unexpected error while updating note")
        raise {"message" : f"Internal server error, {str(error)}"}

def metadata_connector():
    output = get_note_structure()
    logger.info("metadata showed")
    return {"metadata": output, "message": "Metadata showed"}