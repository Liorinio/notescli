import json
from pathlib import Path
from pydantic import BaseModel
from app_types.NoteBase import NoteBase
from app_types.NoteModels import NoteBookMark, NoteSimple, NoteList
from app_types.NoteRegistery import NOTE_INFO
from app_types.NoteType import NoteType

class Db(BaseModel):
    db_data: list[NoteBase | NoteSimple | NoteBookMark | NoteList]
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
        Path(file_path).write_text(self.model_dump_json(indent=4),encoding="utf-8")

    @classmethod
    def load_from_json(cls, file_path: str) -> "Db":
        path = Path(file_path)

        if not path.exists() or path.stat().st_size == 0:
            return cls(db_data=[], counter=0)

        json_data = path.read_text(encoding="utf-8")

        data = json.loads(json_data)

        data["db_data"] = [
            NOTE_INFO[NoteType(note["note_type"])][0].model_validate(note)
            for note in data["db_data"]
        ]

        return cls.model_validate(data)
