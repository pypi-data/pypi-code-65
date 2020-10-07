import os
from ...common_main import common_main


def main() -> None:
    """
    Command that lists all available commands in "sprints" section.

    :return: No return.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    common_main(path)
