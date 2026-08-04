import json
from pathlib import Path
from notecli.note_dict import NoteDict

class DbFileStorage:
    @staticmethod
    def save_to_db(nt: NoteDict, file_path: str):
        data = {
            "db_data": nt.db_data,
            "counter": nt.counter
        }

        Path(file_path).write_text(json.dumps(data, indent=4, default=lambda obj : obj.name))

    @staticmethod
    def load_from_json(file_path: str) -> NoteDict:
        path = Path(file_path)

        if not path.exists() or path.stat().st_size == 0:
            return NoteDict(db_data=[], counter=0)

        data = json.loads(path.read_text(encoding="utf-8"))

        return NoteDict(
            db_data=data["db_data"],
            counter=data["counter"]
        )
