from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.sql.schema import MetaData, Table, Column, CheckConstraint
from sqlalchemy import Integer, String, Enum, DateTime, create_engine

from notecli.app_types.NoteType import NoteType

engine = create_engine('postgresql://notes_user:FirstUserNotes1!@localhost:5432/notesDb')
connection = engine.connect()

print("connected successfully")

metadata = MetaData()

notes = Table("my_table", metadata,
                 Column("id", Integer, primary_key=True),
                       Column("title", String, nullable=False),
                       Column("note_type", Enum(NoteType, nullable=False)),
                       Column("created_at", DateTime, nullable=False),
                       Column("created_at", DateTime, nullable=False),
                       Column("content", JSONB, nullable=False))

Counter = Table("my_table", metadata,
                   Column("id", Integer, primary_key=True),
                         Column("counter", Integer, nullable=False),
                         CheckConstraint("id = 1", name="single_row"))

metadata.create_all(engine)
print("tables created")