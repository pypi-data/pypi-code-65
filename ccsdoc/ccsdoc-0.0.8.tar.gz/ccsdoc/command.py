from typing import List, Optional

from ccsdoc.parameter import Argument
from ccsdoc.text import clean_command_type
from ccsdoc.text import clean_command_level
from ccsdoc.text import clean_description

COMMAND_HEADER: str = "class,name,type,level,description,arguments\n"


class Command:
    def __init__(self, name: str, cmdtype: str, level: str, description: str, args: Optional[List[Argument]] = None) -> None:
        self.name = name
        self.type = clean_command_type(cmdtype)
        self.level = clean_command_level(level)
        self.description = clean_description(description)
        self.args = args if args else []

    def __repr__(self) -> str:
        return f"{self.name}: {self.description}"

    def __str__(self) -> str:
        arg_str = ", ".join([repr(arg) for arg in self.args])

        return (
            f"{self.__class__.__name__}["
            f"name={self.name}, "
            f"type={self.type}, "
            f"level={self.level}, "
            f"desc='{self.description}'"
            f"{', args=(' + arg_str + ')' if arg_str else ''}"
            "]"
        )

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def to_csv(self, class_name: str) -> str:
        return (
            f"{class_name},"
            f"{self.name},"
            f"{self.type},"
            f"{self.level},"
            f"{self.description},"
            f"{';'.join([repr(arg) for arg in self.args])}"
            "\n"
        )
