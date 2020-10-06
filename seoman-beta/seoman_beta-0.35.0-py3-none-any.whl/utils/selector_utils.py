import inquirer  # type: ignore
from typing import List, Any
from .config_utils import ALL_GRANULARITIES


def create_selector(key: str, message: str, choices: List) -> Any:
    """
    Create a dropdown menu that.
    """

    questions = [inquirer.List(name=key, message=message, choices=choices)]
    answer = inquirer.prompt(questions)
    return answer[key]


def create_granularity_selector() -> str:

    questions = [
        inquirer.List(
            name="granularity",
            message="Select a frequency/granularity or group your queries",
            choices=ALL_GRANULARITIES,
        )
    ]
    answer = inquirer.prompt(questions)
    return answer["granularity"]

