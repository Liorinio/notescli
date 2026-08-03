import json
from pathlib import Path
from notecli.note_dict import NoteDict
from notecli.app_types.NoteBase import NoteBase
from notecli.app_types.NoteRegistery import NOTE_INFO
from notecli.app_types.NoteType import NoteType
from notecli.db_schema import Db



class DbFileStorage:
    @staticmethod
    def save_to_db(nt: NoteDict, file_path: str):
        Path(file_path).write_text(json.dumps(nt, indent=4))

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