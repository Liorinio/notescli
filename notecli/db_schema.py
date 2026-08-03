import json
from pathlib import Path
from pydantic import BaseModel, ConfigDict

from notecli.note_dict import NoteDict
from notecli.app_types.NoteBase import NoteBase
from notecli.app_types.NoteRegistery import NOTE_INFO
from notecli.app_types.NoteType import NoteType

class Db(BaseModel):
    model_config = ConfigDict(revalidate_instances="never")

    db_data: list[NoteBase]
    counter: int

    def get_counter(self) -> int:
        return self.counter

    def set_counter(self, value: int) -> None:
        self.counter = value

    def update_counter_by_one(self) -> None:
        self.counter += 1

    def get_db_data(self) -> list[NoteBase]:
        return self.db_data

    def set_db_data(self, data: list[NoteBase]) -> None:
        self.db_data = data

    def add_note_to_db(self, note: NoteBase) -> None:
        self.db_data.append(note)

    def save_to_json(self, file_path: str) -> None:
        Path(file_path).write_text(self.model_dump_json(indent=4,serialize_as_any=True),encoding="utf-8")

    @classmethod
    def load_from_json(cls, file_path: str) -> "Db":
        path = Path(file_path)

        if not path.exists() or path.stat().st_size == 0:
            return cls(db_data=[], counter=0)

        data = json.loads(path.read_text(encoding="utf-8"))

        notes: list[NoteBase] = []

        for note_data in data["db_data"]:
            note_type = NoteType(note_data["note_type"])
            note_class = NOTE_INFO[note_type][0]

            note = note_class.model_validate(note_data)
            notes.append(note)

        return cls(db_data=notes,counter=data["counter"])

    def parse_to_dict(self) -> NoteDict:
        return {
            "db_data": [
                note.model_dump(serialize_as_any=True) for note in self.db_data
            ], "counter": self.counter
        }

    @classmethod
    def parse_from_dict(cls, data_dict: NoteDict):
        notes: list[NoteBase] = []

        for note_data in data_dict["db_data"]:
            note_type = NoteType(note_data["note_type"])
            note_class = NOTE_INFO[note_type][0]

            note = note_class.model_validate(note_data)
            notes.append(note)

        return cls(db_data=notes,counter=data_dict["counter"])
