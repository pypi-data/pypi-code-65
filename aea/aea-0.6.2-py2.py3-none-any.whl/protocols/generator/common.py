# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
"""This module contains utility code for generator modules."""
import inspect
import os
import re
import shutil
import subprocess  # nosec
import sys
from typing import Tuple

from aea.configurations.base import ProtocolSpecification
from aea.configurations.loader import ConfigLoader


SPECIFICATION_PRIMITIVE_TYPES = ["pt:bytes", "pt:int", "pt:float", "pt:bool", "pt:str"]
SPECIFICATION_COMPOSITIONAL_TYPES = [
    "pt:set",
    "pt:list",
    "pt:dict",
    "pt:union",
    "pt:optional",
]
PYTHON_COMPOSITIONAL_TYPES = [
    "FrozenSet",
    "Tuple",
    "Dict",
    "Union",
    "Optional",
]

MESSAGE_IMPORT = "from aea.protocols.base import Message"
SERIALIZER_IMPORT = "from aea.protocols.base import Serializer"

PATH_TO_PACKAGES = "packages"
INIT_FILE_NAME = "__init__.py"
PROTOCOL_YAML_FILE_NAME = "protocol.yaml"
MESSAGE_DOT_PY_FILE_NAME = "message.py"
DIALOGUE_DOT_PY_FILE_NAME = "dialogues.py"
CUSTOM_TYPES_DOT_PY_FILE_NAME = "custom_types.py"
SERIALIZATION_DOT_PY_FILE_NAME = "serialization.py"

PYTHON_TYPE_TO_PROTO_TYPE = {
    "bytes": "bytes",
    "int": "int32",
    "float": "float",
    "bool": "bool",
    "str": "string",
}

CURRENT_DIR = os.path.dirname(inspect.getfile(inspect.currentframe()))  # type: ignore
ISORT_CONFIGURATION_FILE = os.path.join(CURRENT_DIR, "isort.cfg")
ISORT_CLI_ARGS = [
    "--settings-path",
    ISORT_CONFIGURATION_FILE,
    "--quiet",
]


def _to_camel_case(text: str) -> str:
    """
    Convert a text in snake_case format into the CamelCase format.

    :param text: the text to be converted.
    :return: The text in CamelCase format.
    """
    return "".join(word.title() for word in text.split("_"))


def _camel_case_to_snake_case(text: str) -> str:
    """
    Convert a text in CamelCase format into the snake_case format.

    :param text: the text to be converted.
    :return: The text in CamelCase format.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def _match_brackets(text: str, index_of_open_bracket: int) -> int:
    """
    Give the index of the matching close bracket for the opening bracket at 'index_of_open_bracket' in the input 'text'.

    :param text: the text containing the brackets.
    :param index_of_open_bracket: the index of the opening bracket.

    :return: the index of the matching closing bracket (if any).
    :raises SyntaxError if there are no matching closing bracket.
    """
    if text[index_of_open_bracket] != "[":
        raise SyntaxError(
            "Index {} in 'text' is not an open bracket '['. It is {}".format(
                index_of_open_bracket, text[index_of_open_bracket],
            )
        )

    open_bracket_stack = []
    for index in range(index_of_open_bracket, len(text)):
        if text[index] == "[":
            open_bracket_stack.append(text[index])
        elif text[index] == "]":
            open_bracket_stack.pop()
        if not open_bracket_stack:
            return index
    raise SyntaxError(
        "No matching closing bracket ']' for the opening bracket '[' at {} "
        + str(index_of_open_bracket)
    )


def _has_matched_brackets(text: str) -> bool:
    """
    Evaluate whether every opening bracket '[' in the 'text' has a matching closing bracket ']'.

    :param text: the text.
    :return: Boolean result, and associated message.
    """
    open_bracket_stack = []
    for index, _ in enumerate(text):
        if text[index] == "[":
            open_bracket_stack.append(index)
        elif text[index] == "]":
            if len(open_bracket_stack) == 0:
                return False
            open_bracket_stack.pop()
    return len(open_bracket_stack) == 0


def _get_sub_types_of_compositional_types(compositional_type: str) -> Tuple[str, ...]:
    """
    Extract the sub-types of compositional types.

    This method handles both specification types (e.g. pt:set[], pt:dict[]) as well as python types (e.g. FrozenSet[], Union[]).

    :param compositional_type: the compositional type string whose sub-types are to be extracted.
    :return: tuple containing all extracted sub-types.
    """
    sub_types_list = list()
    for valid_compositional_type in (
        SPECIFICATION_COMPOSITIONAL_TYPES + PYTHON_COMPOSITIONAL_TYPES
    ):
        if compositional_type.startswith(valid_compositional_type):
            inside_string = compositional_type[
                compositional_type.index("[") + 1 : compositional_type.rindex("]")
            ].strip()
            while inside_string != "":
                do_not_add = False
                if inside_string.find(",") == -1:  # No comma; this is the last sub-type
                    provisional_sub_type = inside_string.strip()
                    if (
                        provisional_sub_type == "..."
                    ):  # The sub-string is ... used for Tuple, e.g. Tuple[int, ...]
                        do_not_add = True
                    else:
                        sub_type = provisional_sub_type
                    inside_string = ""
                else:  # There is a comma; this MAY not be the last sub-type
                    sub_string_until_comma = inside_string[
                        : inside_string.index(",")
                    ].strip()
                    if (
                        sub_string_until_comma.find("[") == -1
                    ):  # No open brackets; this is a primitive type and NOT the last sub-type
                        sub_type = sub_string_until_comma
                        inside_string = inside_string[
                            inside_string.index(",") + 1 :
                        ].strip()
                    else:  # There is an open bracket'['; this is a compositional type
                        try:
                            closing_bracket_index = _match_brackets(
                                inside_string, inside_string.index("[")
                            )
                        except SyntaxError:
                            raise SyntaxError(
                                "Bad formatting. No matching close bracket ']' for the open bracket at {}".format(
                                    inside_string[
                                        : inside_string.index("[") + 1
                                    ].strip()
                                )
                            )
                        sub_type = inside_string[: closing_bracket_index + 1].strip()
                        the_rest_of_inside_string = inside_string[
                            closing_bracket_index + 1 :
                        ].strip()
                        if (
                            the_rest_of_inside_string.find(",") == -1
                        ):  # No comma; this is the last sub-type
                            inside_string = the_rest_of_inside_string.strip()
                        else:  # There is a comma; this is not the last sub-type
                            inside_string = the_rest_of_inside_string[
                                the_rest_of_inside_string.index(",") + 1 :
                            ].strip()
                if not do_not_add:
                    sub_types_list.append(sub_type)
            return tuple(sub_types_list)
    raise SyntaxError(
        "{} is not a valid compositional type.".format(compositional_type)
    )


def _union_sub_type_to_protobuf_variable_name(
    content_name: str, content_type: str
) -> str:
    """
    Given a content of type union, create a variable name for its sub-type for protobuf.

    :param content_name: the name of the content
    :param content_type: the sub-type of a union type

    :return: The variable name
    """
    if content_type.startswith("FrozenSet"):
        sub_type = _get_sub_types_of_compositional_types(content_type)[0]
        expanded_type_str = "set_of_{}".format(sub_type)
    elif content_type.startswith("Tuple"):
        sub_type = _get_sub_types_of_compositional_types(content_type)[0]
        expanded_type_str = "list_of_{}".format(sub_type)
    elif content_type.startswith("Dict"):
        sub_type_1 = _get_sub_types_of_compositional_types(content_type)[0]
        sub_type_2 = _get_sub_types_of_compositional_types(content_type)[1]
        expanded_type_str = "dict_of_{}_{}".format(sub_type_1, sub_type_2)
    else:
        expanded_type_str = content_type

    protobuf_variable_name = "{}_type_{}".format(content_name, expanded_type_str)

    return protobuf_variable_name


def _python_pt_or_ct_type_to_proto_type(content_type: str) -> str:
    """
    Convert a PT or CT from python to their protobuf equivalent.

    :param content_type: the python type
    :return: The protobuf equivalent
    """
    if content_type in PYTHON_TYPE_TO_PROTO_TYPE.keys():
        proto_type = PYTHON_TYPE_TO_PROTO_TYPE[content_type]
    else:
        proto_type = content_type
    return proto_type


def _includes_custom_type(content_type: str) -> bool:
    """
    Evaluate whether a content type is a custom type or has a custom type as a sub-type.

    :param content_type: the content type
    :return: Boolean result
    """
    if content_type.startswith("Optional"):
        sub_type = _get_sub_types_of_compositional_types(content_type)[0]
        result = _includes_custom_type(sub_type)
    elif content_type.startswith("Union"):
        sub_types = _get_sub_types_of_compositional_types(content_type)
        result = False
        for sub_type in sub_types:
            if _includes_custom_type(sub_type):
                result = True
                break
    elif (
        content_type.startswith("FrozenSet")
        or content_type.startswith("Tuple")
        or content_type.startswith("Dict")
        or content_type in PYTHON_TYPE_TO_PROTO_TYPE.keys()
    ):
        result = False
    else:
        result = True
    return result


def is_installed(programme: str) -> bool:
    """
    Check whether a programme is installed on the system.

    :param programme: the name of the programme.
    :return: True if installed, False otherwise
    """
    res = shutil.which(programme)
    return res is not None


def check_prerequisites() -> None:
    """
    Check whether a programme is installed on the system.

    :return: None
    """
    # check black code formatter is installed
    if not is_installed("black"):
        raise FileNotFoundError(
            "Cannot find black code formatter! To install, please follow this link: https://black.readthedocs.io/en/stable/installation_and_usage.html"
        )

    # check isort code formatter is installed
    if not is_installed("isort"):
        raise FileNotFoundError(
            "Cannot find isort code formatter! To install, please follow this link: https://pycqa.github.io/isort/#installing-isort"
        )

    # check protocol buffer compiler is installed
    if not is_installed("protoc"):
        raise FileNotFoundError(
            "Cannot find protocol buffer compiler! To install, please follow this link: https://developers.google.com/protocol-buffers/"
        )


def load_protocol_specification(specification_path: str) -> ProtocolSpecification:
    """
    Load a protocol specification.

    :param specification_path: path to the protocol specification yaml file.
    :return: A ProtocolSpecification object
    """
    config_loader = ConfigLoader(
        "protocol-specification_schema.json", ProtocolSpecification
    )
    protocol_spec = config_loader.load_protocol_specification(open(specification_path))
    return protocol_spec


def _create_protocol_file(
    path_to_protocol_package: str, file_name: str, file_content: str
) -> None:
    """
    Create a file in the generated protocol package.

    :param path_to_protocol_package: path to the file
    :param file_name: the name of the file
    :param file_content: the content of the file

    :return: None
    """
    pathname = os.path.join(path_to_protocol_package, file_name)

    with open(pathname, "w") as file:
        file.write(file_content)


def try_run_black_formatting(path_to_protocol_package: str) -> None:
    """
    Run Black code formatting via subprocess.

    :param path_to_protocol_package: a path where formatting should be applied.
    :return: None
    """
    subprocess.run(  # nosec
        [sys.executable, "-m", "black", path_to_protocol_package, "--quiet"],
        check=True,
    )


def try_run_isort_formatting(path_to_protocol_package: str) -> None:
    """
    Run Isort code formatting via subprocess.

    :param path_to_protocol_package: a path where formatting should be applied.
    :return: None
    """
    subprocess.run(  # nosec
        [sys.executable, "-m", "isort", *ISORT_CLI_ARGS, path_to_protocol_package],
        check=True,
    )


def try_run_protoc(path_to_generated_protocol_package, name) -> None:
    """
    Run 'protoc' protocol buffer compiler via subprocess.

    :param path_to_generated_protocol_package: path to the protocol buffer schema file.
    :param name: name of the protocol buffer schema file.

    :return: A completed process object.
    """
    subprocess.run(  # nosec
        [
            "protoc",
            "-I={}".format(path_to_generated_protocol_package),
            "--python_out={}".format(path_to_generated_protocol_package),
            "{}/{}.proto".format(path_to_generated_protocol_package, name),
        ],
        stderr=subprocess.PIPE,
        encoding="utf-8",
        check=True,
        env=os.environ.copy(),
    )


def check_protobuf_using_protoc(
    path_to_generated_protocol_package, name
) -> Tuple[bool, str]:
    """
    Check whether a protocol buffer schema file is valid.

    Validation is via trying to compile the schema file. If successfully compiled it is valid, otherwise invalid.
    If valid, return True and a 'protobuf file is valid' message, otherwise return False and the error thrown by the compiler.

    :param path_to_generated_protocol_package: path to the protocol buffer schema file.
    :param name: name of the protocol buffer schema file.

    :return: Boolean result and an accompanying message
    """
    try:
        try_run_protoc(path_to_generated_protocol_package, name)
        os.remove(os.path.join(path_to_generated_protocol_package, name + "_pb2.py"))
        return True, "protobuf file is valid"
    except subprocess.CalledProcessError as e:
        pattern = name + ".proto:[0-9]+:[0-9]+: "
        error_message = re.sub(pattern, "", e.stderr[:-1])
        return False, error_message
