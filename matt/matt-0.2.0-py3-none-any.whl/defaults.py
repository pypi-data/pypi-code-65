# This file is part of Matt.

# Copyright © 2020 Noisytoot
# MATT - MATT Arithmetic Training Test: Another maths test, this time in Python!

# Matt is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Matt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Matt.  If not, see <https://www.gnu.org/licenses/>

from typing import Union
from operator import add, sub, mul


# Default settings for difficulties
def difficulty(namespace: str, number: int) -> Union[dict, None]:
    if namespace == "default":
        if number == 1:
            return {
                "operations": ["+", "-"],
                "maximum": 10,
                "minimum": 0
            }
        elif number == 2:
            return {
                "operations": ["+", "-", "*", "/"],
                "maximum": 20,
                "minimum": 0
            }
    return None


def matt_division(n1, n2):
    correct_answer = n1
    n1 = correct_answer * n2
    return correct_answer


operations: dict = {
    "+": {
        "function": add
    },
    "-": {
        "function": sub
    },
    "*": {
        "function": mul
    },
    "/": {
        "function": matt_division
    }
}
