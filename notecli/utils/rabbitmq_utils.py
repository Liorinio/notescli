from notecli.app_types.json_request_models import NOTE_CREATE_FIELDS
from notecli.app_types.note_type import NoteType
from notecli.app_types.rabbitmq_validation_models import UpdateNoteParams
from notecli.constants import REQUIRED_FIELD, FIRST_NOT_AVAILABLE_FIELD, SECOND_NOT_AVAILABLE_FIELD


def request_content_checker_rabbit_update(note: UpdateNoteParams) -> str | list[str] | None:
    if note["text"] is not None:
        return note["text"]
    elif note["list"] is not None:
        return note["list"]
    elif note["url"] is not None:
        return str(note["url"])
    return None


def check_note_create_parameters_rabbit_update(note: UpdateNoteParams, note_type: NoteType):
        return (__are_fields_not_exist_for_type_rabbit__(note, note_type) and __check_type_content_match_rabbit__(note,note_type)
                and __check_title_rabbit__(note) and __check_is_type_exist_rabbit__(note))


def __check_type_content_match_rabbit__(note: UpdateNoteParams, note_type: NoteType):
    if note["note_type"] != note_type:
        return False
    content_field = NOTE_CREATE_FIELDS[note_type][REQUIRED_FIELD]
    return getattr(note, content_field, None) is not None


def __check_title_rabbit__(note: UpdateNoteParams):
    return note["title"] is not None


def __check_is_type_exist_rabbit__(note: UpdateNoteParams):
    return note["note_type"] is not None


def __are_fields_not_exist_for_type_rabbit__(note: UpdateNoteParams, note_type: NoteType):
    if note["note_type"] != note_type:
        return False
    possible_exist_first_content_attr = getattr(note, NOTE_CREATE_FIELDS[note_type][FIRST_NOT_AVAILABLE_FIELD], None)
    possible_exist_second_content_attr = getattr(note, NOTE_CREATE_FIELDS[note_type][SECOND_NOT_AVAILABLE_FIELD], None)

    return possible_exist_first_content_attr is None and possible_exist_second_content_attr is None
