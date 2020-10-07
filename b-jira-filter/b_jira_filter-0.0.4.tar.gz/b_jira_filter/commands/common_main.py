from os import listdir
from os.path import isfile, join, isdir, basename
from typing import List, Callable


def common_main(path: str) -> None:
    """
    Command that lists all available commands in given path.

    :param path: Path to show all available commands (files).

    :return: No return.
    """
    items = [join(path, name) for name in listdir(path)]

    """
    Check what are the available commands.
    """

    checks = [
        lambda x: x.endswith('.py')
    ]

    commands = __available_actions(checks, [basename(item) for item in items if isfile(item)])
    if commands:
        print('\nAvailable commands:')
        print(commands)

    """
    Check what are the available sections.
    """

    sections = __available_actions([], [basename(item) for item in items if isdir(item)])
    if sections:
        print('\nAvailable sections:')
        print(sections)


def __available_actions(checks: List[Callable[[str], bool]], items: List[str]) -> str:
    """
    Lists available actions (commands or sections).

    :param checks: A list of functions that check whether the file is an action.
    :param items: Available files as actions.

    :return: Human readable text of available actions.
    """
    checks.append(lambda x: not x.startswith('__'))
    checks.append(lambda x: x != 'main.py')

    commands = []
    for item in items:
        if all([check(item) for check in checks]):
            item = item.replace('.py', '')
            item = f'- {item}'

            commands.append(item)

    return '\n'.join(commands)
