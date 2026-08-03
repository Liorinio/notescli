import logging
from typing import Any
import requests
from app_types.NoteBase import NoteBase

logger = logging.getLogger(__name__)

class NoteSimple(NoteBase):
    content: str

    def to_str(self):
        return NoteBase.to_str(self) + f', content: {self.content}'

class NoteList(NoteBase):
    content: list[str]

    def to_str(self):
        return NoteBase.to_str(self) + f', content: {self.content}'


class NoteBookMark(NoteBase):
    content_site_url: str

    def to_str(self):
        return NoteBase.to_str(self) + f', content: {self.content_site_url}'

    # Checks if the content is actual url
    # If so, returns a pair of status code and response body of the response, else return none
    def open_url(self) -> tuple[int, Any] | None:
        url = self.content_site_url.split("://")
        if url[0] == "http" or url[0] == "https":
            response = requests.get(self.content_site_url)
            return response.status_code, response.json()
        return None
