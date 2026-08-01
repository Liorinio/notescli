import os
from datetime import datetime
from typing import Union
import logging
from app_types.NoteBase import NoteBase
from app_types.NoteRegistery import NOTE_INFO
from app_types.NoteType import NoteType
from app_types.NoteModels import NoteSimple, NoteList, NoteBookMark
from db_schema import Db

logger = logging.getLogger(__name__)

def __create_note_by_type__(note_type: NoteType, title: str, content: Union[str, list[str]]) -> NoteSimple | NoteList | NoteBookMark:
    creation_date: datetime = datetime.now()
    note_class, expected_type, note_class_name = NOTE_INFO[note_type]

    if not isinstance(content, expected_type):
        logger.error(f"Invalid type of content, required a {expected_type}")
        raise TypeError(f"The content must be a {expected_type}")
    logger.info(f"A {note_class_name} note was created")
    return note_class(note_id= -1, title=title,note_type=note_type, created_at=creation_date,updated_at=creation_date, content=content)


def __json_to_dict__(db_path: str) -> list[NoteBase]:
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        return []
    db_data: list[NoteBase] = Db.load_from_json(db_path).get_db_data()
    logger.info("The data was retrieved")
    return db_data

def __add_to_db__(new_data: NoteSimple | NoteList | NoteBookMark, db_path: str) -> None:
    db: Db = Db.load_from_json(db_path)
    note_id = db.get_counter()
    db.update_counter_by_one()
    new_data.set_id(note_id)
    db.add_note_to_db(new_data)
    db.save_to_json(db_path)

def __parse_notes__(db_path: str) -> list[NoteBase]:
    if not (os.path.exists(db_path) and os.path.getsize(db_path) > 0):
        logger.error(f"there is no file at the path: ${db_path}")
        return []
    db: Db = Db.load_from_json(db_path)
    return db.get_db_data()


def adder(note_type: NoteType, title: str, content: Union[str, list[str]], db_path: str):
    note = __create_note_by_type__(note_type, title, content)
    __add_to_db__(note, db_path)

def print_all():
    data = __parse_notes__("db2.json")
    for note in data:
        print(note.to_str())
