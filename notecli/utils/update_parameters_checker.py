from notecli.app_types.json_request_models import NoteCreate, NoteUpdate, NOTE_CREATE_FIELDS, NoteBaseRequest
from notecli.app_types.note_type import NoteType


def __are_fields_not_exist_for_type__(note: NoteCreate | NoteUpdate, note_type: NoteType):
    if note.type != note_type:
        return False
    possible_exist_first_content_attr = getattr(note, NOTE_CREATE_FIELDS[note_type][0])
    possible_exist_second_content_attr = getattr(note, NOTE_CREATE_FIELDS[note_type][1])

    return possible_exist_first_content_attr is None and possible_exist_second_content_attr is None


def __check_type_content_match__(note: NoteCreate | NoteUpdate, note_type: NoteType):
    if note.type != note_type:
        return False
    content_field = NOTE_CREATE_FIELDS[note_type][2]
    return content_field is not None


def __check_title__(note: NoteCreate | NoteUpdate):
    return note.title is not None


def __check_is_type_exist__(note: NoteCreate | NoteUpdate):
    return note.type is not None

def check_note_create_parameters(note_create: NoteBaseRequest, note_type: NoteType):
    return (__are_fields_not_exist_for_type__(note_create, note_type) and __check_type_content_match__(note_create, note_type)
            and __check_title__(note_create) and __check_is_type_exist__(note_create))