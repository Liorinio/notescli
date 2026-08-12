from datetime import datetime
import logging
from typing import Any, Self
import requests
from notecli.app_types.NoteBase import NoteBase
from notecli.app_types.NoteType import serializedDict, NoteType, union_of_serialized_notes

logger = logging.getLogger(__name__)

class NoteSimple(NoteBase):
    content: str

    def __init__(self, title: str, note_type: NoteType, content: str, creation_time: datetime):
        super().__init__(title, note_type, creation_time)
        self.content = content

    def to_str(self):
        return NoteBase.to_str(self) + f', content: {self.content}'

    def serialize(self) -> serializedDict:
        ser_dict = super().serialize()
        ser_dict["content"] = self.content
        return ser_dict

    def deserialize(self, data: union_of_serialized_notes) -> Self:
        super().deserialize(data)

        raw_content = data["content"]
        if isinstance(raw_content, str):
            self.content = raw_content

        return self

    def set_content(self, content: str):
        self.content = content

class NoteList(NoteBase):
    content: list[str]

    def __init__(self, title: str, note_type: NoteType, content: list[str], creation_time: datetime):
        super().__init__(title, note_type, creation_time)
        self.content = content

    def to_str(self):
        return NoteBase.to_str(self) + f', content: {self.content}'

    def serialize(self) -> serializedDict:
        ser_dict = super().serialize()
        ser_dict["content"] = self.content
        return ser_dict

    def deserialize(self, data: union_of_serialized_notes) -> Self:
        super().deserialize(data)

        raw_content = data["content"]
        if isinstance(raw_content, list):
            self.content = raw_content

        return self

    def set_content(self, content: list[str]):
        self.content = content


class NoteBookMark(NoteBase):
    content_site_url: str

    def __init__(self, title: str, note_type: NoteType, content: str, creation_time: datetime):
        super().__init__(title, note_type, creation_time)
        self.content_site_url = content

    def to_str(self):
        return NoteBase.to_str(self) + f', content: {self.content_site_url}'

    def serialize(self) -> serializedDict:
        ser_dict = super().serialize()
        ser_dict["content"] = self.content_site_url
        return ser_dict

    def deserialize(self, data: union_of_serialized_notes) -> Self:
        super().deserialize(data)

        raw_content = data["content"]
        if isinstance(raw_content, str):
            self.content_site_url = raw_content

        return self

    def set_content(self, content: str):
        self.content_site_url = content

    # Checks if the content is actual url
    # If so, returns a pair of status code and response body of the response, else return none
    def open_url(self) -> tuple[int, Any] | None:
        if not self.content_site_url.startswith(("http://", "https://")):
            return None

        response = requests.get(self.content_site_url)

        try:
            content = response.json()
        except requests.exceptions.JSONDecodeError:
            content = response.text

        return response.status_code, content
