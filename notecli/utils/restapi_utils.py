import yaml
import os
from dotenv import load_dotenv
from fastapi import Request
import logging
from notecli.app_types.json_request_models import NoteCreate


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
