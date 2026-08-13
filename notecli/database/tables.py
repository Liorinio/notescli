import logging
from datetime import datetime
from typing import Union
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.sql.schema import CheckConstraint
from sqlalchemy import DateTime, create_engine
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = logging.getLogger(__name__)


engine = create_engine('postgresql+psycopg://notes_user:FirstUserNotes1!@localhost:5432/notesDb')
connection = engine.connect()

logger.info("connected successfully to the postgres db")


class Base(DeclarativeBase):
    pass

class Note(Base):
    __tablename__ = "notes"

    note_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    note_type: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    content: Mapped[Union[str, list[str]]] = mapped_column(JSONB, nullable=False)


class Counter(Base):
    __tablename__ = "counter_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    counter: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (CheckConstraint("id = 1", name="single_row"),)

Base.metadata.create_all(engine)
logger.info("Tables created successfully")