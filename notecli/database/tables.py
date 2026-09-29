import logging
import os
from datetime import datetime
from typing import Union, Any
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.sql.schema import CheckConstraint
from sqlalchemy import DateTime, create_engine
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = logging.getLogger(__name__)


load_dotenv()
engine = create_engine(os.environ["POSTGRES_DATABASE_URL"])
connection = engine.connect()

logger.info("connected successfully to the postgres db, layer: table creation")


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

    def __init__(self, note_id: int, title: str, note_type: int, created_at: datetime, updated_at: datetime,
                 content: Union[str, list[str]], **kw: Any):
        super().__init__(**kw)
        self.note_id = note_id
        self.title = title
        self.note_type = note_type
        self.created_at = created_at
        self.updated_at = updated_at
        self.content = content


class Counter(Base):
    __tablename__ = "counter_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    counter: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (CheckConstraint("id = 1", name="single_row"),)

    def __init__(self, id: int, counter: int, **kw: Any):
        super().__init__(**kw)
        self.id = id
        self.counter = counter

Base.metadata.create_all(engine)
logger.info("Tables created successfully, layer: table creation")