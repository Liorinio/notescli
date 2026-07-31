import json
import os
from datetime import datetime
from typing import Union
from uuid import uuid4
import logging
from app_types.NoteBase import NoteBase
from app_types.NoteSchemas import unionOfData, NoteData
from app_types.NoteType import NoteType, serializedDict
from app_types.NoteModels import NoteSimple, NoteList, NoteBookMark
from db_schema import Db


logger = logging.getLogger(__name__)

def __create_note_by_type2__(note_type: NoteType, title: str, content: Union[str, list[str]], db_path: str) -> NoteSimple | NoteList| NoteBookMark:
    db: Db = Db.load_from_json(db_path)
    note_id = db.get_counter()
    creation_date: datetime = datetime.now()

    db.update_counter_by_one()
    db.save_to_json(db_path)

    NOTE_INFO = {
        NoteType.SIMPLE: (NoteSimple, str, "Simple"),
        NoteType.BOOKMARK: (NoteBookMark, str, "BookMark"),
        NoteType.LISTNOTE: (NoteList, list, "List")
    }

    note_class, expected_type, note_class_name = NOTE_INFO[note_type]

    if not isinstance(content, expected_type):
        logger.error(f"Invalid type of content, required a {expected_type}")
        raise TypeError(f"The content must be a {expected_type}")
    logger.info(f"A {note_class_name} note was created")
    return note_class(note_id=note_id, title=title,note_type=note_type, created_at=creation_date,updated_at=creation_date, content=content)
'''
    if note_type == NoteType.SIMPLE:
        if not isinstance(content, str):
            logger.error("Invalid type of content, required a string")
            raise TypeError("Content must be a string")

        logger.info("A Simple note was created")
        return NoteSimple(note_id=note_id, title=title,note_type=note_type, created_at=creation_date,
                          updated_at=creation_date, content=content)
    elif note_type == NoteType.BOOKMARK:
        if not isinstance(content, str):
            logger.error("Invalid type of content, required a string")
            raise TypeError("Content must be a string")

        logger.info("A BookMark note was created")
        return NoteSimple(note_id=note_id, title=title,note_type=note_type, created_at=creation_date,
                          updated_at=creation_date, content=content)
    else:
        if not isinstance(content, list):
            logger.error("Invalid type of content, required a list")
            raise TypeError("Content must be a list")

        logger.info("A List note was created")
        return NoteList(note_id=note_id, title=title, note_type=note_type, created_at=creation_date,
                        updated_at=creation_date, content=content)
'''

def __create_note_by_type__(note_type: NoteType, title: str, content: Union[str, list[str]]) -> NoteSimple | NoteList| NoteBookMark:
    note_id: int = uuid4().int
    creation_date: datetime = datetime.now()

    if note_type == NoteType.SIMPLE:
        if not isinstance(content, str):
            logger.error("Invalid type of content, required a string")
            raise TypeError("Content must be a string")

        logger.info("A Simple note was created")
        return NoteSimple(note_id=note_id, title=title,note_type=note_type, created_at=creation_date,
                          updated_at=creation_date, content=content)
    elif note_type == NoteType.BOOKMARK:
        if not isinstance(content, str):
            logger.error("Invalid type of content, required a string")
            raise TypeError("Content must be a string")

        logger.info("A BookMark note was created")
        return NoteSimple(note_id=note_id, title=title,note_type=note_type, created_at=creation_date,
                          updated_at=creation_date, content=content)
    else:
        if not isinstance(content, list):
            logger.error("Invalid type of content, required a list")
            raise TypeError("Content must be a list")

        logger.info("A List note was created")
        return NoteList(note_id=note_id, title=title, note_type=note_type, created_at=creation_date,
                        updated_at=creation_date, content=content)


def __json_to_dict2__(db_path: str) -> list[NoteBase]:
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        return []
    db_data: list[NoteBase] = Db.load_from_json(db_path).get_db_data()
    logger.info("The data was retrieved")
    return db_data

def __json_to_dict__(db_path: str) -> list[serializedDict]:
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        return []

    with open(db_path, "r") as file:
        try:
            return json.load(file)
        except json.decoder.JSONDecodeError:
            logger.error("the string does not conform to standard JSON format rules")
            return []

def __add_to_db__(new_data:serializedDict, db_path: str) -> None:
    try:
        with open(db_path, "r") as file:
            db_data: list[serializedDict] = json.load(file)
    except(FileNotFoundError, json.decoder.JSONDecodeError):
        db_data = []

    db_data.append(new_data)

    with open(db_path, "w") as file:
        json.dump(db_data, file, indent=4)


def __add_to_db2__(new_data: NoteSimple | NoteList| NoteBookMark, db_path: str) -> None:
    db: Db = Db.load_from_json(db_path)
    db.add_note_to_db(new_data)
    db.save_to_json(db_path)

def adder(note_type: NoteType, title: str, content: Union[str, list[str]]):
    note: serializedDict = __create_note_by_type__(note_type, title, content).serialize()
    __add_to_db__(note, "db.json")

def adder2(note_type: NoteType, title: str, content: Union[str, list[str]], db_path: str):
    note2 = __create_note_by_type2__(note_type, title, content, db_path)
    __add_to_db2__(note2, db_path)


def parse_note(db_path: str) -> list[NoteBase]:
    note_classes: dict[NoteType, type[NoteBase]] = {
        NoteType.SIMPLE: NoteSimple,
        NoteType.BOOKMARK: NoteBookMark,
        NoteType.LISTNOTE: NoteList,
    }

    if not (os.path.exists(db_path) and os.path.getsize(db_path) > 0):
        logger.error(f"there is no file at the path: ${db_path}")
        return []

    with open(db_path, "r") as file:
        raw: list[NoteData | unionOfData] = json.load(file)

    notes: list[NoteBase] = []

    for note in raw:
        note_type = NoteType[note["note_type"]]
        note_class = note_classes[note_type]
        notes.append(note_class.deserialize(note))

    return notes

def parse_notes2(db_path: str) -> list[NoteBase]:
    note_classes: dict[NoteType, type[NoteBase]] = {
        NoteType.SIMPLE: NoteSimple,
        NoteType.BOOKMARK: NoteBookMark,
        NoteType.LISTNOTE: NoteList,
    }

    if not (os.path.exists(db_path) and os.path.getsize(db_path) > 0):
        logger.error(f"there is no file at the path: ${db_path}")
        return []
    db: Db = Db.load_from_json(db_path)
    return db.get_db_data()

def printall2():
    data = parse_notes2("db2.json")
    for note in data:
        print(note.to_str())


def print_all():
    data = parse_note("db.json")
    for note in data:
        print(note.to_str())
