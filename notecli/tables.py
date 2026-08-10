from typing import Union
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.sql.schema import CheckConstraint
from sqlalchemy import Enum, DateTime, create_engine
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from notecli.app_types.NoteType import NoteType

engine = create_engine('postgresql://notes_user:FirstUserNotes1!@localhost:5432/notesDb')
connection = engine.connect()

print("connected successfully")


class Base(DeclarativeBase):
    pass

class Note(Base):
    __tablename__ = "notes"

    note_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    note_type: Mapped[NoteType] = mapped_column(Enum(NoteType), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    content: Mapped[Union[str, list[str]]] = mapped_column(JSONB, nullable=False)


class Counter(Base):
    __tablename__ = "my_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    counter: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (CheckConstraint("id = 1", name="single_row"))

Base.metadata.create_all(engine)
print("Tables created successfully")