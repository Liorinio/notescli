import logging
from typing import Any, Self
import requests
from notecli.app_types.NoteBase import NoteBase
from notecli.app_types.NoteType import serializedDict, NoteType

logger = logging.getLogger(__name__)

class NoteSimple(NoteBase):
    content: str

    def __init__(self, title: str, note_type: NoteType, content: str):
        super().__init__(title, note_type)
        self.content = content

    def to_str(self):
        return NoteBase.to_str(self) + f', content: {self.content}'

    def serialize(self) -> serializedDict:
        ser_dict = super().serialize()
        ser_dict["content"] = self.content
        return ser_dict

    def deserialize(self, data: dict) -> Self:
        super().deserialize(data)

        raw_content = data.get("content")
        if isinstance(raw_content, str):
            self.content = raw_content

        return self

class NoteList(NoteBase):
    content: list[str]

    def __init__(self, title: str, note_type: NoteType, content: list[str]):
        super().__init__(title, note_type)
        self.content = content

    def to_str(self):
        return NoteBase.to_str(self) + f', content: {self.content}'

    def serialize(self) -> serializedDict:
        ser_dict = super().serialize()
        ser_dict["content"] = self.content
        return ser_dict

    def deserialize(self, data: dict) -> Self:
        super().deserialize(data)

        raw_content = data.get("content")
        if isinstance(raw_content, list):
            self.content = raw_content

        return self


class NoteBookMark(NoteBase):
    content_site_url: str

    def __init__(self, title: str, note_type: NoteType, content: str):
        super().__init__(title, note_type)
        self.content_site_url = content

    def to_str(self):
        return NoteBase.to_str(self) + f', content: {self.content_site_url}'

    def serialize(self) -> serializedDict:
        ser_dict = super().serialize()
        ser_dict["content"] = self.content_site_url
        return ser_dict

    def deserialize(self, data: dict) -> Self:
        super().deserialize(data)

        raw_content = data.get("content")
        if isinstance(raw_content, str):
            self.content_site_url = raw_content

        return self


    # Checks if the content is actual url
    # If so, returns a pair of status code and response body of the response, else return none
    def open_url(self) -> tuple[int, Any] | None:
        url = self.content_site_url.split("://")
        if url[0] == "http" or url[0] == "https":
            response = requests.get(self.content_site_url)
            return response.status_code, response.json()
        return None
