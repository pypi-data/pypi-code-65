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

import argparse, secrets, platform, sys, signal, os

from matt.termcolor_wrapper import colored, cprint

import matt.exitcodes as exitcodes
import matt.defaults as defaults

from xdg.BaseDirectory import xdg_config_home  # type: ignore
from pathlib import Path
config_file: str = os.path.join(xdg_config_home, "matt", "config.py")
config: dict = {}
try:
    exec(Path(config_file).read_text(), config)
except FileNotFoundError:
    pass

# Initiali(s|z)e colorama (ANSI escape emulation on windows) (windows only)
if platform.system() == "Windows":
    import colorama  # type: ignore
    colorama.init()

# Try to import readline (must be done after termcolor/colorama imports due to use of cprint)
try:
    import readline  # noqa: F401
except ImportError:
    cprint("Warning: failed to import readline", "red", file=sys.stderr)
    pass

# Parse command line arguments
parser = argparse.ArgumentParser(prog="matt", description="A maths test program")
parser.add_argument("-m", "--minimum", help="The minimum number", type=str)
parser.add_argument("-M", "--maximum", help="The maximum number", type=str)
parser.add_argument("-o", "--operations",
                    help='Allowed operations ("+", "-", "*", "/", or any custom operation), seperated by commas', type=str)
parser.add_argument("-d", "--difficulty", help="Difficulty profile (preset of minimum, maximum, and operations)", type=str)
parser.add_argument("-q", "--question-amount", help="Amount of questions", type=int)
args = parser.parse_args()


def sigint_exit(_signal, _frame):
    print("\nSIGINT caught, exiting…")
    sys.exit(exitcodes.SUCCESS)


def sigterm_exit(_signal, _frame):
    print("\nSIGTERM caught, exiting…")
    sys.exit(exitcodes.SUCCESS)


signal.signal(signal.SIGINT, sigint_exit)
signal.signal(signal.SIGTERM, sigterm_exit)


def isfloat(number) -> bool:
    try:
        float(number)
        return True
    except ValueError:
        return False


def get_answer(operations, operation, n1, n2) -> str:
    formatstr: str = operations[operation].get(
        "format",
        lambda n1, n2: f"{n1} {operation} {n2}"
    )(n1, n2)
    if not operations[operation].get("format_full_override", False):
        formatstr = "What is " + formatstr + "? "
    if not operations[operation].get("format_colour_override", False):
        formatstr = colored(formatstr, "cyan", attrs=["bold"])
    return input(formatstr)


def discard(s_: set, e) -> set:
    s = s_
    s.discard(e)
    return s


def randint_except_0(minimum: int, maximum: int) -> int:
    return secrets.choice(list(discard(set(range(minimum, maximum)), 0)))


def do_level(namespace: str, number: int, question_amount: int):
    if "difficulty" in config and config["difficulty"](namespace, number) is not None:
        difficulty = config["difficulty"](namespace, number)
    else:
        difficulty = defaults.difficulty(namespace, number)

    # Merge default operations and operations from config
    if "operations" not in config:
        config["operations"] = {}
    operations: dict = {**defaults.operations, **config["operations"]}

    # Set value for minimum and maximum from arguments and default
    try:
        difficulty["minimum"] = int(args.minimum)
    except TypeError:
        if "minimum" not in difficulty:
            difficulty["minimum"] = 0
    try:
        difficulty["maximum"] = int(args.maximum)
    except TypeError:
        if "maximum" not in difficulty:
            difficulty["maximum"] = difficulty["minimum"] + 10
    try:
        difficulty["operations"] = args.operations.split(",")
    except AttributeError:
        if "operations" not in difficulty:
            difficulty["operations"] = ["+", "-", "*", "/"]

    score: float = 0
    question: int = 0
    while question < question_amount:
        # Generate random operation
        operation: str = secrets.choice(difficulty["operations"])

        # Generate 2 random numbers
        try:
            n1 = randint_except_0(difficulty["minimum"], difficulty["maximum"])
            n2 = randint_except_0(difficulty["minimum"], difficulty["maximum"])
        except IndexError:
            message = f"""\
Fatal Error: minimum cannot be equivalent to maximum
minimum = {difficulty["minimum"]}
maximum = {difficulty["maximum"]}\
"""
            sys.exit(colored(message, "red", attrs=["bold"]))

        # Set correct answer
        if operation in operations:
            correct_answer = operations[operation]["function"](n1, n2)
        elif not set(difficulty["operations"]).isdisjoint(operations):
            cprint(f'Error: unknown operation "{operation}", skipping question…', "red", file=sys.stderr)
            continue
        else:
            cprint("Error: Difficulty's operations contain nothing but nonsense!", "red", attrs=["bold"], file=sys.stderr)
            sys.exit(exitcodes.NOTHING_BUT_NONSENSE)

        # Get the user's answer
        answer_str: str = ""
        while not isfloat(answer_str):
            answer_str = get_answer(operations, operation, n1, n2)
        answer: float = float(answer_str)
        del answer_str

        # Check the user's answer
        if correct_answer == answer:
            cprint("Correct!", "green", attrs=["bold"])
            score += 1
        elif abs(correct_answer - answer) <= 2:
            points = (1 - 1 / (difficulty["maximum"] ** 2 + 1)) / 2
            cprint(f"Not quite right, the correct answer was {correct_answer}, you get {points} points.", "yellow", attrs=["bold"])
            score += points
        else:
            cprint(f"Wrong, the correct answer was {correct_answer}.", "red", attrs=["bold"])
            question_amount += 1

        # Increment the question
        question += 1
    cprint(f"Your score was {score}/{question_amount}.", "yellow", attrs=["bold"])


difficulty: list = ["default", 1]
try:
    difficulty = args.difficulty.split(":")
except AttributeError:
    cprint(f"Warning: difficulty not set, defaulting to {difficulty[0]}:{difficulty[1]}", "red", file=sys.stderr)

question_amount: int = 10
try:
    question_amount = int(args.question_amount)
except TypeError:
    cprint(f"Warning: amount of questions not set, defaulting to {question_amount}", "red", file=sys.stderr)

do_level(difficulty[0], int(difficulty[1]), question_amount)

# Deinitiali(s|z)e colorama (windows only)
if platform.system() == "Windows":
    colorama.deinit()
