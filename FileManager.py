import json
from pathlib import Path
from typing import TypedDict, Any
from NoteDict import NoteDict
from app_types.NoteBase import NoteBase
from app_types.NoteRegistery import NOTE_INFO
from app_types.NoteType import NoteType
from db_schema import Db



class DbFileStorage:
    @staticmethod
    def save_to_db(db: Db, file_path: str):
        data: NoteDict  = {
            "db_data": [note.model_dump(mode="json") for note in db.db_data],
            "counter": db.counter
        }

        Path(file_path).write_text(json.dumps(data, indent=4))

    @classmethod
    def load_from_json(cls, file_path: str) -> "NoteDict":
        path = Path(file_path)

        if not path.exists() or path.stat().st_size == 0:
            return NoteDict(db_data=[], counter=0)

        data = json.loads(path.read_text(encoding="utf-8"))

        notes: list[NoteBase] = []

        for note_data in data["db_data"]:
            note_type = NoteType(note_data["note_type"])
            note_class = NOTE_INFO[note_type][0]

            note = note_class.model_validate(note_data)
            notes.append(note)

        return NoteDict(db_data=[note.model_dump() for note in notes], counter=data["counter"])