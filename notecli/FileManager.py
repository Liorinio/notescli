import json
import logging
from pathlib import Path
from sqlalchemy import text, create_engine, select
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.sql.schema import Sequence
from notecli.app_types.NoteRegistery import NOTE_INFO
from notecli.app_types.NoteType import NoteType
from notecli.note_store import NoteStore
from notecli.tables import Note, Counter
from sqlalchemy.orm import Session
from notecli.app_types.NoteBase import NoteBase

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
            notes: list[NoteBase] = []

            for row in rows:
                note_class, expected_type, note_class_name = NOTE_INFO[NoteType(row["note_type"])]

                if not isinstance(row["content"], expected_type):
                    logger.error(f"Invalid type of content, required a {expected_type}")
                    raise TypeError(f"The content's type must be of a type: {expected_type}")

                logger.info(f"A {note_class_name} note was created")

                notes.append(note_class(title=row["title"],note_type=NoteType(row["note_type"]),content=row["content"],creation_time=row["created_at"]))

            with PostgresDb.connection as conn:
                db_counter = conn.execute(text("SELECT counter FROM counter_table WHERE id = 1")).scalar_one()
            return NoteStore(db_data=notes, counter=db_counter)

    @staticmethod
    def save_to_db(note_store: NoteStore):
        notes: list[NoteBase] = note_store.get_db_data()

        with Session(PostgresDb.engine) as session:
            memory_ids = {note.note_id for note in notes}

            for note in notes:
                existing_note = session.get(Note, note.note_id)

                if existing_note is None:
                    new_note = Note(
                        note_id=note.note_id,
                        title=note.title,
                        note_type=note.note_type.value,
                        created_at=note.created_at,
                        updated_at=note.updated_at,
                        content=getattr(note, "content"))

                    session.add(new_note)

                    logger.info(f"Note number: {note.note_id} was added to the postgres db")

                else:
                    existing_note.title = note.title
                    existing_note.note_type = note.note_type.value
                    existing_note.created_at = note.created_at
                    existing_note.updated_at = note.updated_at
                    existing_note.content =getattr(note, "content")

                    logger.info(f"Note number: {note.note_id} was updated in the postgres db")

            postgres_ids = session.scalars(select(Note.note_id)).all()

            for note_id in postgres_ids:
                if note_id not in memory_ids:
                    deleted_note = session.get(Note, note_id)
                    session.delete(deleted_note)
                    logger.info(f"Note number: {note_id} was deleted from the postgres db")

            counter = session.get(Counter, 1)

            if counter is None:
                counter = Counter(id=1,counter=note_store.get_counter())
                session.add(counter)

                logger.info("Counter was added to the postgres db")
            else:
                counter.counter = note_store.get_counter()

                logger.info("Counter was updated in the postgres db")

            session.commit()