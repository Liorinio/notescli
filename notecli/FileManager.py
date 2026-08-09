import json
import logging
from pathlib import Path
from typing import Any, Optional
from sqlalchemy import text, create_engine
from notecli.app_types.NoteRegistery import NOTE_INFO
from notecli.note_dict import NoteDict
import psycopg

logger = logging.getLogger(__name__)

class DbFileStorage:
    @staticmethod
    def save_to_db(nt: NoteDict, file_path: str):
        data = {"db_data": nt.get_db_data(),"counter": nt.get_counter()}

        Path(file_path).write_text(json.dumps(data, indent=4, default=lambda obj : obj.name))
        logger.info(f"The database was saved to a file in the following path: {file_path}")

    @staticmethod
    def load_from_db(file_path: str) -> NoteDict:
        path = Path(file_path)

        if not path.exists() or path.stat().st_size == 0:
            logger.info(f"The database wasn't existed in following path: {file_path}, hence it was created")
            return NoteDict(db_data=[], counter=0)

        data = json.loads(path.read_text(encoding="utf-8"))
        logger.info(f"The database was read from the following path: {file_path}")
        return NoteDict(db_data=data["db_data"],counter=data["counter"])


def get_connection():
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="notesDb",
        user="notes_user",  # or postgres
        password="MySecurePassword123!"
    )
    return conn

def table_creator(conn: Any):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                note_type INT NOT NULL
                created_at DATETIME
                updated_at DATETIME
                content TEXT
            )
        """)

        cur.execute("""
         CREATE TABLE IF NOT EXISTS counter_table (
            counter INT
         )
        """)
        conn.commit()

class PostgresStorage:
    @staticmethod
    def save_to_db(nt: NoteDict, conn: psycopg.Connection):
        with conn.cursor() as cur:
            for note in nt.get_db_data():
                cur.execute("""
                    INSERT INTO notes (id, title, note_type, created_at, updated_at, content)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    note["id"],
                    note["title"],
                    note["note_type"],
                    note["created_at"],
                    note["updates_at"],
                    note["content"]
                ))

            cur.execute(
                """
                INSERT INTO counter_table (counter)
                VALUES (%s)
                """,
                (nt.get_counter(),)
            )
        conn.commit()


    @staticmethod
    def load_from_db(conn: psycopg.Connection) -> NoteDict:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, note_type, created_at, updated_at, content
                FROM notes
                ORDER BY id
            """)

            notes = [
                {
                    "id": row[0],
                    "title": row[1],
                    "note_type": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                    "content": row[5]

                }
                for row in cur.fetchall()
            ]

            cur.execute("SELECT counter FROM counter_table")
            row: Optional[tuple[int]] = cur.fetchone()

            counter = 0 if row is None else row[0]
            return NoteDict(notes, counter)


class PostgresDb:
    @staticmethod
    def load_from_db():
        engine = create_engine('postgresql://notes_user:FirstUserNotes1!@localhost:5432/notesDb')
        connection = engine.connect()
        rows = connection.execute(text("SELECT * FROM notes")).mappings().all()

        notes: list[dict[str, Any]] = []

        for row in rows:
            note_class, expected_type, note_class_name = NOTE_INFO[row["note_type"]]

            if not isinstance(row["content"], expected_type):
                logger.error(f"Invalid type of content, required a {expected_type}")
                raise TypeError(f"The content must be a {expected_type}")
            logger.info(f"A {note_class_name} note was created")
            return note_class(title=row["title"], note_type=row["note_type"], content=row["content"])

        with connection as conn:
            query = text("SELECT your_int_column FROM your_table WHERE id = 1")
            db_counter = conn.execute(query).scalar_one()
        return NoteDict(db_data=notes, counter=db_counter)



