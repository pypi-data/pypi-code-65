import argparse
from convo.cli.arguments import default_arguments
from convo.cli.arguments.run import add_server_arguments
from convo.constants import DEFAULT_CONVO_X_PORT
from convo.shared.constants import DEFAULT_DATA_PATH


def set_x_arguments(parser: argparse.ArgumentParser):
    default_arguments.add_model_param(parser, add_positional_arg=False)

    default_arguments.add_data_param(
        parser, default=DEFAULT_DATA_PATH, data_type="stories and Convo NLU "
    )
    default_arguments.add_config_param(parser)

    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Automatic yes or default options to prompts and oppressed warnings.",
    )

    parser.add_argument(
        "--production",
        action="store_true",
        help="Run Convo X in a production environment.",
    )

    parser.add_argument(
        "--convo-x-port",
        default=DEFAULT_CONVO_X_PORT,
        type=int,
        help="Port to run the Convo X server at.",
    )

    parser.add_argument(
        "--config-endpoint",
        type=str,
        help="Convo X endpoint URL from which to pull the runtime config. This URL "
        "typically contains the Convo X token for authentication. Example: "
        "https://example.com/api/config?token=my_convo_x_token",
    )

    add_server_arguments(parser)
