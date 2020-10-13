import pprint as pretty_print
import typing
from typing import Any, Dict, Optional, Text

from convo.core.interpreter import ConvoNLUInterpreter
from convo.shared.nlu.interpreter import NaturalLanguageInterpreter
from convo.shared.utils.cli import print_error, print_success
import convo.utils.common

if typing.TYPE_CHECKING:
    from convo.core.agent import Agent


def pprint(obj: Any):
    pretty_print.pprint(obj, indent=2)


def chat(
    model_path: Optional[Text] = None,
    endpoints: Optional[Text] = None,
    agent: Optional["Agent"] = None,
    interpreter: Optional[NaturalLanguageInterpreter] = None,
) -> None:
    """Chat to the bot within a Jupyter notebook.

    Args:
        model_path: Path to a combined Convo model.
        endpoints: Path to a yaml with the action server is custom actions are defined.
        agent: Convo Core agent (used if no Convo model given).
        interpreter: Convo NLU interpreter (used with Convo Core agent if no
                     Convo model is given).
    """

    if model_path:
        from convo.run import create_agent

        agent = create_agent(model_path, endpoints)

    elif agent is not None and interpreter is not None:
        # HACK: this skips loading the interpreter and directly
        # sets it afterwards
        nlu_interpreter = ConvoNLUInterpreter(
            "skip this and use given interpreter", lazy_init=True
        )
        nlu_interpreter.interpreter = interpreter
        agent.interpreter = interpreter
    else:
        print_error(
            "You either have to define a model path or an agent and an interpreter."
        )
        return

    print("Your bot is ready to talk! Type your messages here or send '/stop'.")
    while True:
        message = input()
        if message == "/stop":
            break

        responses = convo.utils.common.run_in_loop(agent.handle_text(message))
        for response in responses:
            _display_bot_response(response)


def _display_bot_response(response: Dict):
    from IPython.display import Image, display  # pytype: disable=import-error

    for response_type, value in response.items():
        if response_type == "text":
            print_success(value)

        if response_type == "image":
            image = Image(url=value)
            display(image)
