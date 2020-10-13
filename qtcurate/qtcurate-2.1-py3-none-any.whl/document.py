from typing import Dict
from qtcurate.qt import Qt
from smart_open import open
from qtcurate.exceptions import QtArgumentError
from qtcurate.utilities import connect, json_to_tuple


class Document:

    def __init__(self):
        self.headers = {"X-API-Key": Qt.api_key}
        self.url = Qt.url
        self.id = None

    def __repr__(self):
        return f"{self.id}"

    def set_id(self, uuid: str) -> None:
        if isinstance(uuid, str):
            self.id = uuid
        else:
            raise QtArgumentError("Argument type error: String is expected as uuid")

    def get_id(self) -> str:
        return self.id

    def create(self, file: str) -> str:
        """Upload files for data mining"""
        if not isinstance(file, str):
            raise QtArgumentError("Argument type error: String is expected as file path")
        files = {'file': open(file, 'rb')}
        res = connect("post", f"{self.url}search/file", self.headers, "files", files)
        doc = json_to_tuple(res.json())
        return doc.uuid
