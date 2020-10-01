import os
import sys
from typing import Dict, Sequence, Text, Tuple

ansicolors: Dict[Text, Text] = {
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "LIGHT_CYAN": "\033[1;36m",
    "WHITE": "\033[37m",
    "BOLD": "\033[1m",
    "RESET": "\033[0m",
}

green_start: Text = ansicolors["GREEN"]
red_start: Text = ansicolors["RED"]
cyan_start: Text = ansicolors["CYAN"]
light_cyan_start: Text = ansicolors["LIGHT_CYAN"]
reset: Text = ansicolors["RESET"]


def path_header(header: str, nocolor=False) -> str:
    header_len = len(header) + 1
    divider_char = "-"
    if not nocolor and sys.stdout.isatty():
        header_string = (
            f"{divider_char * header_len}{os.linesep}"
            f"{light_cyan_start}{header}{reset}{os.linesep}"
            f"{divider_char * header_len}"
        )
    else:
        header_string = (
            f"{divider_char * header_len}{os.linesep}"
            f"{header}{os.linesep}"
            f"{divider_char * header_len}"
        )
    return header_string


def overlap_result(glyphname: str, test_pass: bool, nocolor=False) -> str:
    # color
    if not nocolor and sys.stdout.isatty():
        if test_pass:
            result_pre = f"[ {red_start}{glyphname}{reset} ]: "
        else:
            result_pre = f"[ {green_start}{glyphname}{reset} ]: "
    else:
        result_pre = f"[{glyphname}]: "
    # test pass indicator
    if test_pass:
        result = result_pre + "Yes"
    else:
        result = result_pre + "No"
    return result


def direction_result(
    glyphname: str,
    direction_clockwise: bool,
    contours: int,
    components_with_transforms: Sequence[Tuple] = [],
    nocolor=False,
) -> str:
    if not nocolor and sys.stdout.isatty():
        if contours == 0:
            return f"[ {light_cyan_start}{glyphname}{reset} ]: no contours"
        if direction_clockwise:
            return (
                f"[ {light_cyan_start}{glyphname}{reset} ]: "
                f"clockwise"
                f"{_transformed_component(components_with_transforms)}"
            )
        else:
            return (
                f"[ {light_cyan_start}{glyphname}{reset} ]: "
                f"counter-clockwise"
                f"{_transformed_component(components_with_transforms)}"
            )
    else:
        if contours == 0:
            return f"[ {glyphname} ]: no contours"
        if direction_clockwise:
            return (
                f"[ {glyphname} ]: clockwise"
                f"{_transformed_component(components_with_transforms)}"
            )
        else:
            return (
                f"[ {glyphname} ]: counter-clockwise"
                f"{_transformed_component(components_with_transforms)}"
            )


def _transformed_component(components_with_transforms: Sequence[Tuple]) -> str:
    if len(components_with_transforms) > 0:
        left_pad = " " * 10
        components_string = f"{os.linesep}"
        for x, component in enumerate(components_with_transforms):
            component_glyphname = component[0]
            component_transform = component[1]
            components_string += (
                f"{left_pad}with component '{component_glyphname}' transform: "
                f"{component_transform}"
            )
            if x + 1 < len(components_with_transforms):
                # add newline unless this is the last component in the list
                components_string += f"{os.linesep}"
        return components_string
    else:
        return ""
