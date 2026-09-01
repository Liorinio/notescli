from notecli.app_types.note_models import NoteSimple, NoteBookMark, NoteList
from notecli.app_types.note_type import NoteType

# a dictionary that is used for creating a note in a polymorphic way
NOTE_INFO = {
    NoteType.SIMPLE: (NoteSimple, str, "Simple"),
    NoteType.BOOKMARK: (NoteBookMark, str, "BookMark"),
    NoteType.LISTNOTE: (NoteList, list, "List")
}

# a dictionary that is used for setting and getting the content of a note in a polymorphic way
NOTE_GETTER_SETTER = {
    NoteType.SIMPLE: (NoteSimple.set_content, NoteSimple.get_content),
    NoteType.BOOKMARK: (NoteBookMark.set_content, NoteBookMark.get_content),
    NoteType.LISTNOTE: (NoteList.set_content, NoteList.get_content)

}