from __future__ import annotations
import json
import os
from typing import List
from qtcurate.exceptions import QtArgumentError, QtFileTypeError
from qtcurate.qt import Qt
from qtcurate.utilities import connect


category = "category"
vocab_name = "dict_name"
vocab_id = "dict_id"
type_field = "type"
str_field = "str"
double_value = "doubleValue"
int_value = "intValue"
line = "line"
start = "start"
end = "end"


class Position:
    def __init__(self):
        self.start = None
        self.end = None
        self.line = None

    def set_start(self, pos_start: int) -> Position:
        if isinstance(pos_start, int):
            self.start = pos_start
        else:
            raise QtArgumentError("Argument type error: Int is expected as pos_start")
        return self

    def get_start(self) -> int:
        return self.start

    def set_end(self, pos_end: int) -> Position:
        if isinstance(pos_end, int):
            self.end = pos_end
        else:
            raise QtArgumentError("Argument type error: Int is expected as pos_end")
        return self

    def get_end(self) -> int:
        return self.end

    def set_line(self, pos_line: int) -> Position:
        if isinstance(pos_line, int):
            self.line = pos_line
        else:
            raise QtArgumentError("Argument type error: Int is expected as pos_line")
        return self

    def get_int_value(self) -> int:
        return self.line


class FieldValue:
    def __init__(self):
        self.str_value = None

    def __repr__(self):
        return f"{self.str_value}"

    def set_str(self, str_val: str) -> FieldValue:
        if isinstance(str_val, str):
            self.str_value = str_val
        else:
            raise QtArgumentError("Argument type error: String is expected as str_val")
        return self

    def get_str(self) -> str:
        return self.str_value


class Field:

    def __init__(self):
        self.vocab_name = None
        self.vocab_id = None
        self.category = None
        self.type = None
        self.str = None
        self.values = None
        self.position = None

    def __repr__(self):
        return f"{self.vocab_id}, {self.str}"

    def set_values(self, val: List) -> Field:
        if isinstance(val, list):
            self.values = val
        else:
            raise QtArgumentError("Argument type error: List is expected as val")
        return self

    def get_values(self) -> List:
        return self.values

    def set_str(self, str_value: str) -> Field:
        if isinstance(str_value, str):
            self.str = str_value
        else:
            raise QtArgumentError("Argument type error: String is expected as str_val")
        return self

    def get_str(self) -> str:
        return self.str

    def set_type(self, type_value: str) -> Field:
        if isinstance(type_value, str):
            self.type = type_value
        else:
            raise QtArgumentError("Argument type error: String is expected as type_value")
        return self

    def get_type(self) -> str:
        return self.type

    def set_vocab_name(self, name: str) -> Field:
        if isinstance(name, str):
            self.vocab_name = name
        else:
            raise QtArgumentError("Argument type error: String is expected as name")
        return self

    def get_vocab_name(self) -> str:
        return self.vocab_name

    def set_category(self, cat: str) -> Field:
        if isinstance(cat, str):
            self.category = cat
        else:
            raise QtArgumentError("Argument type error: String is expected as cat")
        return self

    def get_category(self) -> str:
        return self.category

    def set_vocab_id(self, voc_id: str) -> Field:
        if isinstance(voc_id, str):
            self.vocab_id = voc_id
        else:
            raise QtArgumentError("Argument type error: String is expected as voc_id")
        return self

    def get_vocab_id(self) -> str:
        return self.vocab_id

    def set_position(self, position: Position) -> Field:
        if isinstance(position, Position):
            self.position = position
        else:
            raise QtArgumentError("Argument type error: Position is expected as position")
        return self

    def get_position(self) -> Position:
        return self.position


class Result:

    def __init__(self, dp_id):
        self.id = dp_id
        self.headers = {"X-API-Key": Qt.api_key}
        self.url = Qt.url

    def raw_exporter(self, path: str) -> None:
        """Exporting in JSON format"""

        if not isinstance(path, str):
            raise QtArgumentError("Argument type error: String is expected as path")
        directory = os.path.dirname(path)
        if len(directory) == 0:
            directory = "."
        if not (os.access(directory, os.W_OK) and os.access(directory, os.X_OK)):
            raise QtArgumentError("Argument error: No write permission")
        extension = os.path.splitext(path)[1].lower()
        if extension != ".json":
            raise QtFileTypeError("File type error: Please use json extension saving file")
        res = connect("get", f"{self.url}reports/{self.id}/json", self.headers)
        with open(path, "w") as json_file:
            json.dump(res.json(), json_file)

    def result_xlsx_exporter(self, path: str) -> None:
        """Exporting in Excel format"""

        if not isinstance(path, str):
            raise QtArgumentError("Argument type error: String is expected as path")
        directory = os.path.dirname(path)
        if len(directory) == 0:
            directory = "."
        if not (os.access(directory, os.W_OK) and os.access(directory, os.X_OK)):
            raise QtArgumentError("Argument error: No write permission")
        extension = os.path.splitext(path)[1].lower()
        if extension != ".xlsx":
            raise QtFileTypeError("File type error: Please use xlsx extension saving file")
        res = connect("get", f"{self.url}reports/{self.id}/xlsx", self.headers)

        with open(path, 'wb') as excel_file:
            excel_file.write(res.content)

    def read(self) -> List:
        """Convert to Object namedtuple"""
        result_list = []
        res = connect("get", f"{self.url}reports/{self.id}/json", self.headers)
        for item in res.json():
            if "values" in item:
                for i in item["values"]:
                    field = Field()
                    position = Position()
                    if start in i:
                        position.set_start(i[start])
                    if end in i:
                        position.set_end(i[end])
                    if line in i:
                        position.set_line(i[line])
                    field.set_position(position)
                    if str_field in i:
                        field.set_str(i[str_field])
                    if type_field in i:
                        field.set_type(i[type_field])
                    if category in i:
                        field.set_category(i[category])
                    if vocab_name in i:
                        field.set_vocab_name(i[vocab_name])
                    if vocab_id in i:
                        field.set_vocab_id(i[vocab_id])
                    list_field_ext = []
                    if "extIntervalSimples" in i:
                        for ext_int_item in i["extIntervalSimples"]:
                            field_value = FieldValue()
                            if str_field in ext_int_item:
                                field_value.set_str(ext_int_item[str_field])
                            list_field_ext.append(field_value)
                    field.set_values(list_field_ext)
                    result_list.append(field)
        return result_list
