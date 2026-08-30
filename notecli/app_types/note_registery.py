from notecli.app_types.note_models import NoteSimple, NoteBookMark, NoteList
from notecli.app_types.note_type import NoteType

# a dictionary that is used for creating a note in a polymorphic way
NOTE_INFO : dict[NoteType, tuple[type[NoteSimple], type[str], str] | tuple[type[NoteBookMark], type[str], str] | tuple[type[NoteList], type[list], str]] = {
    NoteType.SIMPLE: (NoteSimple, str, "Simple"),
    NoteType.BOOKMARK: (NoteBookMark, str, "BookMark"),
    NoteType.LISTNOTE: (NoteList, list, "List")
}