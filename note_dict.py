from typing import TypedDict, Any


class NoteDict(TypedDict):
    db_data: list[dict[str, Any]]
    counter: int
