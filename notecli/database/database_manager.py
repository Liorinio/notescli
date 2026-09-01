import json
import logging
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import sessionmaker
from notecli.app_types.note_registery import NOTE_INFO
from notecli.app_types.note_type import NoteType
from notecli.memory_storage.note_store import NoteStore
from notecli.database.tables import Note, Counter
from sqlalchemy.orm import Session
from notecli.app_types.note_base import NoteBase
from dotenv import load_dotenv
import os


logger = logging.getLogger(__name__)

class DbFileStorage:
    file_path = "db.json"

    @staticmethod
    def save_to_db(note_store: NoteStore):
        data = {"db_data": note_store["db_data"], "counter": note_store["counter"]}

        Path(DbFileStorage.file_path).write_text(json.dumps(data, indent=4, default=lambda obj : obj.name))
        logger.info(f"The database was saved to a file in the following path: {DbFileStorage.file_path}, layer: DbManager")

    @staticmethod
    def load_from_db() -> NoteStore:
        path = Path(DbFileStorage.file_path)

        if path.exists() and path.stat().st_size != 0:
            data = json.loads(path.read_text(encoding="utf-8"))
            logger.info(f"The database was read from the following path: {DbFileStorage.file_path}, layer: DbManager")
            return NoteStore(db_data=data["db_data"], counter=data["counter"])

        logger.info(f"The database wasn't existed in following path: {DbFileStorage.file_path}, hence it was created, layer: DbManager")
        return NoteStore(db_data=[], counter=Counter(id=1,counter=0))


class PostgresDb:
    load_dotenv()
    engine = create_engine(os.environ["DATABASE_URL"])
    SessionLocal = sessionmaker(bind=engine)

    logger.info("connected successfully to the postgres db, layer: DbManager")

    @staticmethod
    def load_from_db() -> NoteStore:
        try:
            with PostgresDb.SessionLocal() as session:
                #trying to retrieve the counter from the postgres
                try:
                    db_counter: Counter = session.execute(select(Counter)).scalar_one()

                except NoResultFound:
                    db_counter = Counter(id=1, counter=0)

                #retrieving all the notes from the postgres db
                rows = session.scalars(select(Note)).all()

                if not rows:
                    return NoteStore(db_data=[],counter=db_counter)

                logger.info("The data was retrieved from the database, layer: DbManager")
                notes: list[NoteBase] = []

                for row in rows:
                    note_class, expected_type, note_class_name = NOTE_INFO[NoteType(row.note_type)]

                    if not isinstance(row.content, expected_type):
                        logger.error(f"Invalid type of content, required a {expected_type}, layer: DbManager")
                        raise TypeError(f"The content's type must be of a type: {expected_type}, layer: DbManager")

                    logger.info(f"A {note_class_name} note was created")

                    #creating the notes in the memory
                    notes.append(note_class(title=row.title,note_type=NoteType(row.note_type),content=row.content,creation_time=row.created_at))

                return NoteStore(db_data=notes,counter=db_counter)

        except Exception as exception:
            session.close()
            logger.exception(exception)
            raise exception

    @staticmethod
    def save_to_db(note_store: NoteStore,optional_deleted_note_id: int | None = None) -> None:
        try:
            notes: list[NoteBase] = note_store["db_data"]

            with Session(PostgresDb.engine) as session:
                with session.begin():
                    counter = session.get(Counter, 1)


                    if optional_deleted_note_id is not None:
                        PostgresDb.delete_note_for_postgres(optional_deleted_note_id,session)
                    else:
                        PostgresDb.__upsertNote__(notes, session)

                    PostgresDb.__set_db_counter__(counter,session,note_store["counter"].counter)

        except Exception as exception:
            logger.exception("Failed to save notes to PostgreSQL, layer: DbManager")
            raise exception

    @staticmethod
    def __upsertNote__(notes: list[NoteBase], session: Session) -> None:
        """
        Function that checks if the note exists in the Postgres db, if it is, the function updates it, if not, the function creates it.
        """
        for note in notes:
            existing_note = session.get(Note, note.note_id)

            if existing_note is None:
                new_note = Note(note_id=note.note_id, title=note.title, note_type=note.note_type.value,
                                created_at=note.created_at, updated_at=note.updated_at,content=getattr(note, "content", getattr(note, "content_site_url", None)))

                session.add(new_note)
                logger.info(f"Note number: {note.note_id} was added to the postgres db, layer: DbManager")

            else:
                existing_note.title = note.title
                existing_note.note_type = note.note_type.value
                existing_note.created_at = note.created_at
                existing_note.updated_at = note.updated_at
                if hasattr(note, "content"):
                    existing_note.content = note.content
                elif hasattr(note, "content_site_url"):
                    existing_note.content = note.content_site_url

                logger.info(f"Note number: {note.note_id} was updated in the postgres db, layer: DbManager")


    @staticmethod
    def delete_note_for_postgres(removed_note_id: int,session: Session) -> None:
        deleted_note = session.get(Note, removed_note_id)

        if deleted_note is None:
            raise ValueError(f"Note {removed_note_id} does not exist in the database, layer: DbManager")

        session.delete(deleted_note)

        logger.info("Note number %s was deleted from the postgres db, layer: DbManager",removed_note_id)

    @staticmethod
    def __set_db_counter__(counter: Counter | None, session:Session, memory_db_counter: int) -> None:
        """
       Setting the counter of the db in the Postgres db
        """
        if counter is None:
            session.add(Counter(id=1, counter=memory_db_counter))
            logger.info("Counter was added to the postgres db, layer: DbManager")
        else:
            counter.counter = memory_db_counter
            logger.info("Counter was updated in the postgres db, layer: DbManager")
