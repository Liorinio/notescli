from pathlib import Path

from pydantic import BaseModel
from app_types.NoteBase import NoteBase


class Db(BaseModel):
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

    def save_to_json(self, file_path: str) -> None:
        Path(file_path).write_text(self.model_dump_json(indent=4),
            encoding="utf-8")

    @classmethod
    def load_from_json(cls, file_path: str) -> "Db":
        json_data = Path(file_path).read_text(encoding="utf-8")
        return cls.model_validate_json(json_data)

