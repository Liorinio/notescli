import json
import os
from datetime import datetime
from typing import Union, cast, Any
from uuid import uuid4
from app_types.NoteBase import NoteBase
from app_types.NoteData import SimpleData, ListData, BookMarkData, unionOfData, NoteData
from app_types.NoteType import NoteType, serializedDict
from app_types.NoteTypes import NoteSimple, NoteList, NoteBookMark

def __create_note_by_type__(note_type: NoteType, title: str, content: Union[str, list[str]]) -> NoteSimple | NoteList| NoteBookMark:
    node_id: int = uuid4().int
    creation_date: datetime = datetime.now()

    if note_type == NoteType.SIMPLE:
        if not isinstance(content, str):
            raise TypeError("Content must be a string")
        return NoteSimple(note_id=node_id, title=title,note_type=note_type, created_at=creation_date,
                          updated_at=creation_date, content=content)
    elif note_type == NoteType.BOOKMARK:
        if not isinstance(content, str):
            raise TypeError("Content must be a string")
        return NoteSimple(note_id=node_id, title=title,note_type=note_type, created_at=creation_date,
                          updated_at=creation_date, content=content)
    else:
        if not isinstance(content, list):
            raise TypeError("Content must be a list")
        return NoteList(note_id=node_id, title=title, note_type=note_type, created_at=creation_date,
                        updated_at=creation_date, content=content)

def __json_to_dict__(db_path: str) -> list[serializedDict]:
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        return []

    with open(db_path, "r") as file:
        try:
            return json.load(file)
        except json.decoder.JSONDecodeError:
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


def parse_note2(db_path: str) -> list[NoteBase]:
    note_classes: dict[NoteType, type[NoteBase]] = {
        NoteType.SIMPLE: NoteSimple,
        NoteType.BOOKMARK: NoteBookMark,
        NoteType.LISTNOTE: NoteList,
    }

    if not (os.path.exists(db_path) and os.path.getsize(db_path) > 0):
        return []

    with open(db_path, "r") as file:
        raw: list[NoteData | SimpleData | ListData | BookMarkData] = json.load(file)

    notes = []

    for note in raw:
        note_type = NoteType[note["note_type"]]
        note_class = note_classes[note_type]
        notes.append(note_class.deserialize(note))

    return notes



def __parse_notes__(db_path: str) -> list[unionOfData]:
    data: list[unionOfData] = []

    if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
        with open(db_path, "r") as file:
            raw:Any = json.load(file)

        for note in raw:
            note_type: NoteType = NoteType[note["note_type"]]
            match note_type:
                case NoteType.SIMPLE:
                    data.append(cast(SimpleData, note))
                case NoteType.BOOKMARK:
                    data.append(cast(BookMarkData, note))
                case NoteType.LISTNOTE:
                    data.append(cast(ListData, note))
    return data

def print_all():
    data: list[unionOfData] = __parse_notes__("db.json")
    for note_data in data:
        note_type: NoteType = NoteType[note_data["note_type"]]
        if note_type == NoteType.SIMPLE:
            print(NoteSimple.deserialize(note_data).to_str()+"\n")
        elif note_type == NoteType.BOOKMARK:
            print(NoteBookMark.deserialize(note_data).to_str()+"\n")
        else:
            print(NoteList.deserialize(note_data).to_str()+"\n")

def print_all2():
    data = parse_note2("db.json")
    for note in data:
        print(note.to_str())
