from notecli.app_types.note_models import NoteSimple, NoteBookMark, NoteList
from notecli.app_types.rabbitmq_validation_models import NavigateNoteParams, AddNoteParams, DeleteNoteParams, GetAllNotesParams, SearchNoteParams, ViewNoteParams, QueueResponse, UpdateNoteParams
from notecli.services.note_handlers import add_note, delete_note, view_specific_note, navigate_url, update_note, search_note, get_note


def add_connector(add_params: AddNoteParams):
    added_note: NoteSimple | NoteBookMark | NoteList | None = add_note(add_params['given_note_type'], add_params['title'], add_params['content'], add_params['db'])

    if not added_note:
        logger.info("The given requirements didn't allow to create a note of the given type")
        return {"message": "The given requirements didn't allow to create a note of the given type"}
    else:
        logger.info("Note was added")
        return {"message": "Note created successfully", "added note": added_note.to_str()}

def delete_connector(delete_params: DeleteNoteParams):
    ...

def navigate_connector(navigate_params: NavigateNoteParams):
    ...

def get_all_notes_connector(get_notes_params: GetAllNotesParams):
    ...

def search_connector(search_params: SearchNoteParams):
    ...

def view_connector(view_params: SearchNoteParams):
    ...

def update_connector(update_params: UpdateNoteParams):
    ...