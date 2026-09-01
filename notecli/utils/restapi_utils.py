import yaml
import os
from dotenv import load_dotenv
from fastapi import Request
import logging
from notecli.app_types.json_request_models import NoteCreate, NoteUpdate
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


def request_content_checker(note: NoteUpdate | NoteCreate) -> str | list[str] | None:
    if note.text is not None:
        return note.text
    elif note.list is not None:
        return note.list
    elif note.url is not None:
        return str(note.url)
    return None
