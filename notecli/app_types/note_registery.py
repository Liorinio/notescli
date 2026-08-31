from notecli.app_types.note_models import NoteSimple, NoteBookMark, NoteList
from notecli.app_types.note_type import NoteType

# a dictionary that is used for creating a note in a polymorphic way
NOTE_INFO = {
    NoteType.SIMPLE: (NoteSimple, str, "Simple", NoteSimple.set_content),
    NoteType.BOOKMARK: (NoteBookMark, str, "BookMark", NoteBookMark.set_content),
    NoteType.LISTNOTE: (NoteList, list, "List", NoteList.set_content)
}