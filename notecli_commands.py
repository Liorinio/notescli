import json
import os
from datetime import datetime
from typing import Union, cast, Any
from uuid import uuid4
import logging
from app_types.NoteBase import NoteBase
from app_types.NoteSchemas import SimpleData, ListData, BookMarkData, unionOfData, NoteData
from app_types.NoteType import NoteType, serializedDict
from app_types.NoteModels import NoteSimple, NoteList, NoteBookMark

def __create_note_by_type__(note_type: NoteType, title: str, content: Union[str, list[str]]) -> NoteSimple | NoteList| NoteBookMark:
    node_id: int = uuid4().int
    creation_date: datetime = datetime.now()

    if note_type == NoteType.SIMPLE:
        if not isinstance(content, str):
            logging.error("Invalid type of content, required a string")
            raise TypeError("Content must be a string")

        logging.info("A Simple note was created")
        return NoteSimple(note_id=node_id, title=title,note_type=note_type, created_at=creation_date,
                          updated_at=creation_date, content=content)
    elif note_type == NoteType.BOOKMARK:
        if not isinstance(content, str):
            logging.error("Invalid type of content, required a string")
            raise TypeError("Content must be a string")

        logging.info("A BookMark note was created")
        return NoteSimple(note_id=node_id, title=title,note_type=note_type, created_at=creation_date,
                          updated_at=creation_date, content=content)
    else:
        if not isinstance(content, list):
            logging.error("Invalid type of content, required a list")
            raise TypeError("Content must be a list")

        logging.info("A List note was created")
        return NoteList(note_id=node_id, title=title, note_type=note_type, created_at=creation_date,
                        updated_at=creation_date, content=content)

def __json_to_dict__(db_path: str) -> list[serializedDict]:
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        return []

    with open(db_path, "r") as file:
        try:
            return json.load(file)
        except json.decoder.JSONDecodeError:
            logging.error("the string does not conform to standard JSON format rules")
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

def adder(note_type: NoteType, title: str, content: Union[str, list[str]]):
    note: serializedDict = __create_note_by_type__(note_type, title, content).serialize()
    __add_to_db__(note, "db.json")


def parse_note(db_path: str) -> list[NoteBase]:
    note_classes: dict[NoteType, type[NoteBase]] = {
        NoteType.SIMPLE: NoteSimple,
        NoteType.BOOKMARK: NoteBookMark,
        NoteType.LISTNOTE: NoteList,
    }

    if not (os.path.exists(db_path) and os.path.getsize(db_path) > 0):
        logging.error(f"there is no file at the path: ${db_path}")
        return []

    with open(db_path, "r") as file:
        raw: list[NoteData | unionOfData] = json.load(file)

    notes: list[NoteBase] = []

    for note in raw:
        note_type = NoteType[note["note_type"]]
        note_class = note_classes[note_type]
        notes.append(note_class.deserialize(note))

    return notes


def print_all():
    data = parse_note("db.json")
    for note in data:
        print(note.to_str())
