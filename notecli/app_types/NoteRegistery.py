from notecli.app_types.NoteModels import NoteSimple, NoteBookMark, NoteList
from notecli.app_types.NoteType import NoteType

NOTE_INFO : dict[NoteType, tuple[type[NoteSimple], type[str], str] | tuple[type[NoteBookMark], type[str], str] | tuple[type[NoteList], type[list], str]] = {
    NoteType.SIMPLE: (NoteSimple, str, "Simple"),
    NoteType.BOOKMARK: (NoteBookMark, str, "BookMark"),
    NoteType.LISTNOTE: (NoteList, list, "List")
}