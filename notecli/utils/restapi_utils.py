import yaml
import os
from dotenv import load_dotenv
from fastapi import Request
import logging
from notecli.app_types.json_request_models import NoteCreate, NoteUpdate, NOTE_CREATE_FIELDS, NOTE_CREATE_CONTENT_FIELD, \
    NoteBaseRequest
from notecli.app_types.note_type import NoteType

logger = logging.getLogger(__name__)


def replace_openapi():
    load_dotenv()

    with open(os.environ["OPENAPI_FILE_PATH"], "r", encoding="utf-8") as file:
        custom_openapi_schema = yaml.safe_load(file)
    return custom_openapi_schema


async def restapi_middleware(request: Request, call_next):
    logger.info("Before the endpoint, level: restapi_utils")
    response = await call_next(request)
    logger.info("After the endpoint, level: restapi_utils")
    return response


def update_request_content_checker(note_update: NoteUpdate) -> str | list[str] | None:
    if note_update.text is not None:
        return note_update.text
    elif note_update.list is not None:
        return note_update.list
    elif note_update.url is not None:
        return str(note_update.url)
    return None


def create_request_content_checker(note_update: NoteCreate) -> str | list[str] | None:
    if note_update.text is not None:
        return note_update.text
    elif note_update.list is not None:
        return note_update.list
    elif note_update.url is not None:
        return str(note_update.url)
    return None


def __check_type_and_content_match__(note: NoteCreate | NoteUpdate, note_type: NoteType):
    if note.type != note_type:
        return False
    first_check_field = NOTE_CREATE_FIELDS[note_type][0]
    second_check_field = NOTE_CREATE_FIELDS[note_type][1]

    first_attr = getattr(note, first_check_field)
    second_attr = getattr(note, second_check_field)

    return first_attr is None and second_attr is None


def __check_type_content_match__(note: NoteCreate | NoteUpdate, note_type: NoteType):
    if note.type != note_type:
        return False
    content_field = NOTE_CREATE_CONTENT_FIELD[note_type]
    return content_field is not None


def __check_title__(note: NoteCreate | NoteUpdate):
    return note.title is not None


def __check_is_type_exist__(note: NoteCreate | NoteUpdate):
    return note.type is not None

def check_note_create_parameters(note_create: NoteBaseRequest, note_type: NoteType):
    return (__check_type_and_content_match__(note_create, note_type) and __check_type_content_match__(note_create, note_type)
            and __check_title__(note_create) and __check_is_type_exist__(note_create))

def check_type_swamp(note_id: int, note_type: str):
    ...