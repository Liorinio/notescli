import json
import logging
from pathlib import Path
from notecli.note_dict import NoteDict

logger = logging.getLogger(__name__)

class DbFileStorage:
    @staticmethod
    def save_to_db(nt: NoteDict, file_path: str):
        data = {"db_data": nt.get_db_data(),"counter": nt.get_counter()}

        Path(file_path).write_text(json.dumps(data, indent=4, default=lambda obj : obj.name))
        logger.info(f"The database was saved to a file in the following path: {file_path}")

    @staticmethod
    def load_from_json(file_path: str) -> NoteDict:
        path = Path(file_path)

        if not path.exists() or path.stat().st_size == 0:
            logger.info(f"The database wasn't existed in following path: {file_path}, hence it was created")
            return NoteDict(db_data=[], counter=0)

        data = json.loads(path.read_text(encoding="utf-8"))
        logger.info(f"The database was read from the following path: {file_path}")
        return NoteDict(db_data=data["db_data"],counter=data["counter"])
