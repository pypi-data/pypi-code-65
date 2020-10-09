import argparse
import asyncio
import importlib.util
import logging
import os
import signal
import traceback
from multiprocessing import get_context
from typing import List, Text, Optional, Tuple, Iterable

import aiohttp
import ruamel.yaml as yaml

import convo.cli.utils as cli_utils
import convo.utils.io as io_utils
from convo.cli.arguments import x as arguments
from convo.constants import (
    DEFAULT_ENDPOINTS_PATH,
    DEFAULT_CREDENTIALS_PATH,
    DEFAULT_DOMAIN_PATH,
    DEFAULT_CONFIG_PATH,
    DEFAULT_LOG_LEVEL_CONVO_X,
    DEFAULT_CONVO_X_PORT,
    DEFAULT_CONVO_PORT,
    DOCS_BASE_URL_CONVO_X,
)
from convo.core.utils import AvailableEndpoints
from convo.utils.endpoints import EndpointConfig

logger = logging.getLogger(__name__)

DEFAULT_EVENTS_DB = "events.db"


# noinspection PyProtectedMember
def add_subparser(
    subparsers: argparse._SubParsersAction, parents: List[argparse.ArgumentParser]
):
    x_parser_args = {
        "parents": parents,
        "conflict_handler": "resolve",
        "formatter_class": argparse.ArgumentDefaultsHelpFormatter,
    }

    if is_convo_x_installed():
        # we'll only show the help msg for the command if Convo X is actually installed
        x_parser_args["help"] = "Starts the Convo X interface."

    shell_parser = subparsers.add_parser("x", **x_parser_args)
    shell_parser.set_defaults(func=convo_x)

    arguments.set_x_arguments(shell_parser)


def _convo_service(
    args: argparse.Namespace,
    endpoints: AvailableEndpoints,
    convo_x_url: Optional[Text] = None,
    credentials_path: Optional[Text] = None,
):
    """Starts the Convo application."""
    from convo.core.run import serve_application
    import convo.utils.common

    # needs separate logging configuration as it is started in its own process
    convo.utils.common.set_log_level(args.loglevel)
    io_utils.configure_colored_logging(args.loglevel)

    if not credentials_path:
        credentials_path = _prepare_credentials_for_convo_x(
            args.credentials, convo_x_url=convo_x_url
        )

    serve_application(
        endpoints=endpoints,
        port=args.port,
        credentials=credentials_path,
        cors=args.cors,
        auth_token=args.auth_token,
        enable_api=True,
        jwt_secret=args.jwt_secret,
        jwt_method=args.jwt_method,
        ssl_certificate=args.ssl_certificate,
        ssl_keyfile=args.ssl_keyfile,
        ssl_ca_file=args.ssl_ca_file,
        ssl_password=args.ssl_password,
    )


def _prepare_credentials_for_convo_x(
    credentials_path: Optional[Text], convo_x_url: Optional[Text] = None
) -> Text:
    credentials_path = cli_utils.get_validated_path(
        credentials_path, "credentials", DEFAULT_CREDENTIALS_PATH, True
    )
    if credentials_path:
        credentials = io_utils.read_config_file(credentials_path)
    else:
        credentials = {}

    # this makes sure the Convo X is properly configured no matter what
    if convo_x_url:
        credentials["convo"] = {"url": convo_x_url}
    dumped_credentials = yaml.dump(credentials, default_flow_style=False)
    tmp_credentials = io_utils.create_temporary_file(dumped_credentials, "yml")

    return tmp_credentials


def _overwrite_endpoints_for_local_x(
    endpoints: AvailableEndpoints, convo_x_token: Text, convo_x_url: Text
):
    endpoints.model = _get_model_endpoint(endpoints.model, convo_x_token, convo_x_url)
    endpoints.event_broker = _get_event_broker_endpoint(endpoints.event_broker)


def _get_model_endpoint(
    model_endpoint: Optional[EndpointConfig], convo_x_token: Text, convo_x_url: Text
) -> EndpointConfig:
    # If you change that, please run a test with Convo X and speak to the bot
    default_convox_model_server_url = (
        f"{convo_x_url}/projects/default/models/tags/production"
    )

    model_endpoint = model_endpoint or EndpointConfig()

    # Checking if endpoint.yml has existing url, if so give
    # warning we are overwriting the endpoint.yml file.
    custom_url = model_endpoint.url

    if custom_url and custom_url != default_convox_model_server_url:
        logger.info(
            f"Ignoring url '{custom_url}' from 'endpoints.yml' and using "
            f"'{default_convox_model_server_url}' instead."
        )

    custom_wait_time_pulls = model_endpoint.kwargs.get("wait_time_between_pulls")
    return EndpointConfig(
        default_convox_model_server_url,
        token=convo_x_token,
        wait_time_between_pulls=custom_wait_time_pulls or 2,
    )


def _get_event_broker_endpoint(
    event_broker_endpoint: Optional[EndpointConfig],
) -> EndpointConfig:
    import questionary

    default_event_broker_endpoint = EndpointConfig(
        type="sql", dialect="sqlite", db=DEFAULT_EVENTS_DB
    )
    if not event_broker_endpoint:
        return default_event_broker_endpoint
    elif not _is_correct_event_broker(event_broker_endpoint):
        cli_utils.print_error(
            f"Convo X currently only supports a SQLite event broker with path "
            f"'{DEFAULT_EVENTS_DB}' when running locally. You can deploy Convo X "
            f"with Docker ({DOCS_BASE_URL_CONVO_X}/installation-and-setup/"
            f"docker-compose-quick-install/) if you want to use other event broker "
            f"configurations."
        )
        continue_with_default_event_broker = questionary.confirm(
            "Do you want to continue with the default SQLite event broker?"
        ).ask()

        if not continue_with_default_event_broker:
            exit(0)

        return default_event_broker_endpoint
    else:
        return event_broker_endpoint


def _is_correct_event_broker(event_broker: EndpointConfig) -> bool:
    return all(
        [
            event_broker.type == "sql",
            event_broker.kwargs.get("dialect", "").lower() == "sqlite",
            event_broker.kwargs.get("db") == DEFAULT_EVENTS_DB,
        ]
    )


def start_convo_for_local_convo_x(args: argparse.Namespace, convo_x_token: Text):
    """Starts the Convo X API with Convo as a background process."""

    credentials_path, endpoints_path = _get_credentials_and_endpoints_paths(args)
    endpoints = AvailableEndpoints.read_endpoints(endpoints_path)

    convo_x_url = f"http://localhost:{args.convo_x_port}/api"
    _overwrite_endpoints_for_local_x(endpoints, convo_x_token, convo_x_url)

    vars(args).update(
        dict(
            nlu_model=None,
            cors="*",
            auth_token=args.auth_token,
            enable_api=True,
            endpoints=endpoints,
        )
    )

    ctx = get_context("spawn")
    p = ctx.Process(
        target=_convo_service, args=(args, endpoints, convo_x_url, credentials_path)
    )
    p.daemon = True
    p.start()
    return p


def is_convo_x_installed() -> bool:
    """Check if Convo X is installed."""

    # we could also do something like checking if `import convox` works,
    # the issue with that is that it actually does import the package and this
    # takes some time that we don't want to spend when booting the CLI
    return importlib.util.find_spec("convox") is not None


def generate_convo_x_token(length: int = 16):
    """Generate a hexadecimal secret token used to access the Convo X API.

    A new token is generated on every `convo x` command.
    """

    from secrets import token_hex

    return token_hex(length)


def _configure_logging(args: argparse.Namespace):
    from convo.core.utils import configure_file_logging
    from convo.utils.common import set_log_level

    log_level = args.loglevel or DEFAULT_LOG_LEVEL_CONVO_X

    if isinstance(log_level, str):
        log_level = logging.getLevelName(log_level)

    logging.basicConfig(level=log_level)
    io_utils.configure_colored_logging(args.loglevel)

    set_log_level(log_level)
    configure_file_logging(logging.root, args.log_file)

    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("engineio").setLevel(logging.WARNING)
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger("socketio").setLevel(logging.ERROR)

    if not log_level == logging.DEBUG:
        logging.getLogger().setLevel(logging.WARNING)
        logging.getLogger("py.warnings").setLevel(logging.ERROR)


def is_convo_project_setup(args: argparse.Namespace, project_path: Text) -> bool:
    config_path = _get_config_path(args)
    mandatory_files = [config_path, DEFAULT_DOMAIN_PATH]

    for f in mandatory_files:
        if not os.path.exists(os.path.join(project_path, f)):
            return False

    return True


def _validate_convo_x_start(args: argparse.Namespace, project_path: Text):
    if not is_convo_x_installed():
        cli_utils.print_error_and_exit(
            "Convo X is not installed. The `convo x` "
            "command requires an installation of Convo X. "
            "Instructions on how to install Convo X can be found here: "
            "https://convo.com/docs/convo-x/."
        )

    if args.port == args.convo_x_port:
        cli_utils.print_error_and_exit(
            "The port for Convo X '{}' and the port of the Convo server '{}' are the "
            "same. We need two different ports, one to run Convo X (e.g. delivering the "
            "UI) and another one to run a normal Convo server.\nPlease specify two "
            "different ports using the arguments '--port' and '--convo-x-port'.".format(
                args.convo_x_port, args.port
            )
        )

    if not is_convo_project_setup(args, project_path):
        cli_utils.print_error_and_exit(
            "This directory is not a valid Convo project. Use 'convo init' "
            "to create a new Convo project or switch to a valid Convo project "
            "directory (see http://convo.com/docs/convo/user-guide/"
            "convo-tutorial/#create-a-new-project)."
        )

    _validate_domain(os.path.join(project_path, DEFAULT_DOMAIN_PATH))

    if args.data and not os.path.exists(args.data):
        cli_utils.print_warning(
            "The provided data path ('{}') does not exists. Convo X will start "
            "without any training data.".format(args.data)
        )


def _validate_domain(domain_path: Text):
    from convo.core.domain import Domain, InvalidDomain

    try:
        Domain.load(domain_path)
    except InvalidDomain as e:
        cli_utils.print_error_and_exit(
            "The provided domain file could not be loaded. " "Error: {}".format(e)
        )


def convo_x(args: argparse.Namespace):
    from convo.cli.utils import signal_handler

    signal.signal(signal.SIGINT, signal_handler)

    _configure_logging(args)

    if args.production:
        run_in_production(args)
    else:
        run_locally(args)


async def _pull_runtime_config_from_server(
    config_endpoint: Optional[Text],
    attempts: int = 60,
    wait_time_between_pulls: float = 5,
    keys: Iterable[Text] = ("endpoints", "credentials"),
) -> Optional[List[Text]]:
    """Pull runtime config from `config_endpoint`.

    Returns a list of paths to yaml dumps, each containing the contents of one of
    `keys`.
    """

    while attempts:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config_endpoint) as resp:
                    if resp.status == 200:
                        rjs = await resp.json()
                        try:
                            return [
                                io_utils.create_temporary_file(rjs[k]) for k in keys
                            ]
                        except KeyError as e:
                            cli_utils.print_error_and_exit(
                                "Failed to find key '{}' in runtime config. "
                                "Exiting.".format(e)
                            )
                    else:
                        logger.debug(
                            "Failed to get a proper response from remote "
                            "server. Status Code: {}. Response: '{}'"
                            "".format(resp.status, await resp.text())
                        )
        except aiohttp.ClientError as e:
            logger.debug(f"Failed to connect to server. Retrying. {e}")

        await asyncio.sleep(wait_time_between_pulls)
        attempts -= 1

    cli_utils.print_error_and_exit(
        "Could not fetch runtime config from server at '{}'. "
        "Exiting.".format(config_endpoint)
    )


def run_in_production(args: argparse.Namespace):
    from convo.cli.utils import print_success

    print_success("Starting Convo X in production mode... 🚀")

    credentials_path, endpoints_path = _get_credentials_and_endpoints_paths(args)
    endpoints = AvailableEndpoints.read_endpoints(endpoints_path)

    _convo_service(args, endpoints, None, credentials_path)


def _get_config_path(args: argparse.Namespace,) -> Optional[Text]:
    config_path = cli_utils.get_validated_path(
        args.config, "config", DEFAULT_CONFIG_PATH
    )

    return config_path


def _get_credentials_and_endpoints_paths(
    args: argparse.Namespace,
) -> Tuple[Optional[Text], Optional[Text]]:
    config_endpoint = args.config_endpoint
    if config_endpoint:
        loop = asyncio.get_event_loop()
        endpoints_config_path, credentials_path = loop.run_until_complete(
            _pull_runtime_config_from_server(config_endpoint)
        )

    else:
        endpoints_config_path = cli_utils.get_validated_path(
            args.endpoints, "endpoints", DEFAULT_ENDPOINTS_PATH, True
        )
        credentials_path = None

    return credentials_path, endpoints_config_path


def run_locally(args: argparse.Namespace):
    # noinspection PyUnresolvedReferences
    from convox.community import local  # pytype: disable=import-error

    args.convo_x_port = args.convo_x_port or DEFAULT_CONVO_X_PORT
    args.port = args.port or DEFAULT_CONVO_PORT

    project_path = "."

    _validate_convo_x_start(args, project_path)

    local.check_license_and_metrics(args)
    convo_x_token = generate_convo_x_token()
    process = start_convo_for_local_convo_x(args, convo_x_token=convo_x_token)

    config_path = _get_config_path(args)

    try:
        local.main(
            args, project_path, args.data, token=convo_x_token, config_path=config_path
        )
    except Exception:
        print(traceback.format_exc())
        cli_utils.print_error(
            "Sorry, something went wrong (see error above). Make sure to start "
            "Convo X with valid data and valid domain and config files. Please, "
            "also check any warnings that popped up.\nIf you need help fixing "
            "the issue visit our forum: https://forum.convo.com/."
        )
    finally:
        process.terminate()
