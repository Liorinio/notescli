common_metadata_dict = {
    "note_id": ("The id of the note", "needs be of integer type"),
    "title" :("The title of the note", "needs be of string type"),
    "note_type" : ("The type of note", "needs be of NoteType type, the available types of notes: SIMPLE, NOTELIST, BOOKMARK"),
    "created_at" : ("The date which the note was created", "needs be of datetime type"),
    "updated_at" : ("The date which the note was updated", "needs be of datetime type")
}

special_fields_dict = ["The content of a SIMPLE note is a single string", "The content of a NOTELIST note is a list of string", "The content of a BOOKMARK note is a single string"]