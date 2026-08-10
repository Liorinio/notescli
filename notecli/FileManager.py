import json
import logging
from pathlib import Path
from typing import Any
from sqlalchemy import text, create_engine, TextClause
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.sql.schema import Sequence
from notecli.app_types.NoteRegistery import NOTE_INFO
from notecli.note_store import NoteStore
from notecli.tables import Note, Counter
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class DbFileStorage:
    file_path = "db2.json"

    @staticmethod
    def save_to_db(note_store: NoteStore):
        data = {"db_data": note_store.get_db_data(), "counter": note_store.get_counter()}

        Path(DbFileStorage.file_path).write_text(json.dumps(data, indent=4, default=lambda obj : obj.name))
        logger.info(f"The database was saved to a file in the following path: {DbFileStorage.file_path}")

    @staticmethod
    def load_from_db() -> NoteStore:
        path = Path(DbFileStorage.file_path)

        if not path.exists() or path.stat().st_size == 0:
            logger.info(f"The database wasn't existed in following path: {DbFileStorage.file_path}, hence it was created")
            return NoteStore(db_data=[], counter=0)

        data = json.loads(path.read_text(encoding="utf-8"))
        logger.info(f"The database was read from the following path: {DbFileStorage.file_path}")
        return NoteStore(db_data=data["db_data"], counter=data["counter"])

class PostgresDb:
    engine = create_engine('postgresql+psycopg://notes_user:FirstUserNotes1!@localhost:5432/notesDb')
    connection = engine.connect()

    logger.info("connected successfully to the postgres db")

    @staticmethod
    def load_from_db():
        rows: Sequence[RowMapping] = PostgresDb.connection.execute(text("SELECT * FROM notes")).mappings().all()

        if not rows:
            return NoteStore(db_data=[], counter=0)
        else:
            logger.info("The data was retrieved from the database")
            notes: list[dict[str, Any]] = []

            for row in rows:
                note_class, expected_type, note_class_name = NOTE_INFO[row["note_type"]]

                if not isinstance(row["content"], expected_type):
                    logger.error(f"Invalid type of content, required a {expected_type}")
                    raise TypeError(f"The content must be a {expected_type}")
                else:
                    logger.info(f"A {note_class_name} note was created")
                    notes.append(note_class(title=row["title"], note_type=row["note_type"], content=row["content"]))

            with PostgresDb.connection as conn:
                query: TextClause = text("SELECT your_int_column FROM your_table WHERE id = 1")
                db_counter = conn.execute(query).scalar_one()
            return NoteStore(db_data=notes, counter=db_counter)

    @staticmethod
    def save_to_db(note_store: NoteStore):
        with Session(PostgresDb.engine) as session:
            notes = note_store.get_db_data()

            for i in range(len(notes)):
                note = notes[i]
                new_note = Note(note_id=note["note_id"], title= note["title"], note_type= note["note_type"], created_at=note["created_at"], updated_at= note["updated_at"], content=note["content"])
                session.add(new_note)

            new_counter = Counter(id=1, counter=note_store.get_counter())
            session.add(new_counter)

            session.commit()
