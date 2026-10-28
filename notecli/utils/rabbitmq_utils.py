import logging
from typing import Any, cast

from notecli.app_types.json_request_models import NOTE_CREATE_FIELDS
from notecli.app_types.note_type import NoteType
from notecli.app_types.rabbitmq_validation_models import UpdateNoteParams
from notecli.constants import REQUIRED_FIELD, FIRST_NOT_AVAILABLE_FIELD, SECOND_NOT_AVAILABLE_FIELD

logger = logging.Logger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def request_content_checker_rabbit_update(note: UpdateNoteParams) -> str | list[str] | None:
    if note["text"] is not None:
        return note["text"]
    elif note["list"] is not None:
        return note["list"]
    elif note["url"] is not None:
        return str(note["url"])
    return None


def check_note_create_parameters_rabbit_update(note: UpdateNoteParams, db_note_type: NoteType):
    title_ok = __check_title_rabbit__(note)
    content_ok = __check_type_content_match_rabbit__(note, db_note_type)
    fields_ok = __are_fields_not_exist_for_type_rabbit__(note, db_note_type)

    # Let's find out exactly what it wants!
    required_key = NOTE_CREATE_FIELDS[db_note_type][REQUIRED_FIELD]

    logger.info(f"[DEBUG] Title Check: {title_ok}")
    logger.info(f"[DEBUG] Content Check: {content_ok} (It is strictly looking for the key: '{required_key}')")
    logger.info(f"[DEBUG] Extra Fields Check: {fields_ok}")

    return title_ok and content_ok and fields_ok


def __check_type_content_match_rabbit__(note: UpdateNoteParams, db_note_type: NoteType):
    content_field = NOTE_CREATE_FIELDS[db_note_type][REQUIRED_FIELD]
    note_dict = cast(dict[str, Any], note)

    return note_dict.get(content_field) is not None


def __check_title_rabbit__(note: UpdateNoteParams):
    return note.get("title") is not None


def __are_fields_not_exist_for_type_rabbit__(note: UpdateNoteParams, db_note_type: NoteType):
    first_field = NOTE_CREATE_FIELDS[db_note_type][FIRST_NOT_AVAILABLE_FIELD]
    second_field = NOTE_CREATE_FIELDS[db_note_type][SECOND_NOT_AVAILABLE_FIELD]
    note_dict = cast(dict[str, Any], note)

    possible_exist_first = note_dict.get(first_field)
    possible_exist_second = note_dict.get(second_field)

    return possible_exist_first is None and possible_exist_second is None
