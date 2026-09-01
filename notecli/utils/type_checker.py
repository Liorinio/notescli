from notecli.app_types.note_base import NoteBase
from notecli.app_types.note_type import NoteType


def bookmark_url_checker(note: NoteBase, content: str | list[str]):
    if note.note_type is NoteType.BOOKMARK and isinstance(content, str):
        if content.startswith(("http://", "https://")):
            return True
    return False