from typing import Any, Self
import requests
from app_types.NoteBase import NoteBase
from app_types.NoteType import serializedDict, SerializedNote, SerializedNoteSimple
from app_types.NoteData import NoteData, unionOfData


class NoteSimple(NoteBase):
    content: str

    def to_str(self):
        return NoteBase.to_str(self) + f'content: {self.content}'

    def serialize(self) -> serializedDict:
        note_dict: serializedDict = NoteBase.serialize(self)
        note_dict['content'] = self.content
        return note_dict

    @classmethod
    def deserialize(cls, data: SerializedNote) -> NoteSimple:
        if not isinstance(data["content"], str):
            raise TypeError("NotteSimple must contain a string content")
        return cls(**super().deserialize(data).model_dump(), content=data["content"])

class NoteList(NoteBase):
    content: list[str]

    def to_str(self):
        return NoteBase.to_str(self) + f'content: {self.content}'

    def serialize(self) -> serializedDict:
        note_dict: serializedDict = NoteBase.serialize(self)
        note_dict['content'] = self.content
        return note_dict

    @classmethod
    @classmethod
    def deserialize(cls, data: SerializedNote) -> "NoteList":
        if "content" not in data:
            raise TypeError("Missing content")

        content = data["content"]

        if not isinstance(content, list):
            raise TypeError("NoteList must contain a list of strings")

        return cls(
            **super().deserialize(data).model_dump(),
            content=content
        )

class NoteBookMark(NoteBase):
    content_site_url: str

    def to_str(self):
        return NoteBase.to_str(self) + f'content: {self.content_site_url}'

    def serialize(self) -> serializedDict:
        note_dict: serializedDict = NoteBase.serialize(self)
        note_dict['content'] = self.content_site_url
        return note_dict

    @classmethod
    def deserialize(cls, data: NoteData | unionOfData) -> Self:
        if not isinstance(data["content"], str):
            raise TypeError("NotteSimple must contain a string content")
        return cls(**super().deserialize(data).model_dump(), content_site_url=data["content"])

    def open_url(self) -> tuple[int, Any] | None:
        url = self.content_site_url.split("://")
        if url[0] == "http" or url[0] == "https":
            response = requests.get(self.content_site_url)
            return response.status_code, response.json
        return None
