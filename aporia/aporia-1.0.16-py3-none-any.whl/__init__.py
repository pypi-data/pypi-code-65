"""Aporia SDK.

Usage:
    >>> import aporia
    >>> aporia.init(
    >>>     token='12345',
    >>>     host='production.myorg.cloud.aporia.com',
    >>>     port=443,
    >>>     environment="production"
    >>> )
    >>> model = aporia.Model(model_name='my-model'], model_version='v1')
    >>> model.set_features(feature_names=['x1', 'x2', 'x3'], categorical=['x2'])
    >>> model.log_predict(x=[1.3, 0.7, 0.2], y=[0.09])
"""
import atexit
from contextlib import suppress
import logging
import sys
from typing import Optional

from aporia.config import Config
from aporia.consts import LOG_FORMAT, LOGGER_NAME
from aporia.errors import handle_error
from aporia.event_loop import EventLoop
from aporia.graphql_client import GraphQLClient
from aporia.model import Model

try:
    from importlib.metadata import version, PackageNotFoundError  # type: ignore
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError  # type: ignore


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"


__all__ = ["init", "flush", "Model"]


class Context:
    """Global context."""

    def __init__(self, graphql_client: GraphQLClient, event_loop: EventLoop, config: Config):
        """Initializes the context.

        Args:
            graphql_client (GraphQLClient): GraphQL client.
            event_loop (EventLoop): Event loop.
            config (Config): Aporia config.
        """
        self.graphql_client = graphql_client
        self.event_loop = event_loop
        self.config = config


context = None
logger = logging.getLogger(LOGGER_NAME)


def init(
    token: Optional[str] = None,
    host: Optional[str] = None,
    environment: Optional[str] = None,
    port: Optional[int] = None,
    debug: Optional[bool] = None,
    throw_errors: Optional[bool] = None,
    blocking_call_timeout: Optional[int] = None,
):
    """Initializes the Aporia SDK.

    Args:
        token (str): Authentication token.
        host (str): Controller host.
        environment (str): Environment in which aporia is initialized (e.g production, staging).
        port (int, optional): Controller port. Defaults to 443.
        debug (bool, optional): True to enable debug mode - this will cause additional logs
            and stack traces during exceptions. Defaults to False.
        throw_errors (bool, optional): True to cause errors to be raised
            as exceptions. Defaults to False.
        blocking_call_timeout (int, optional): Timeout, in seconds, for blocking aporia API
            calls - Model(), set_features(), add_extra_inputs(), add_extra_outputs().

    Notes:
        * The token, host and environment parameters are required.
        * All of the parameters here can also be defined as environment variables:
            * token -> APORIA_TOKEN
            * host -> APORIA_HOST
            * environment -> APORIA_ENVIRONMENT
            * port -> APORIA_PORT
            * debug -> APORIA_DEBUG
            * throw_errors -> APORIA_THROW_ERRORS
            * blocking_call_timeout -> APORIA_BLOCKING_CALL_TIMEOUT
        * Values passed as parameters to aporia.init() override the values from
          the corresponding environment variables.
    """
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, style="{"))
        logger.addHandler(handler)

    logger.debug("Initializing Aporia SDK.")

    try:
        config = Config(
            token=token,
            host=host,
            environment=environment,
            port=port,
            debug=debug,
            throw_errors=throw_errors,
            blocking_call_timeout=blocking_call_timeout,
        )

        # Init graphql client and event loop
        event_loop = EventLoop()
        graphql_client = GraphQLClient(token=config.token, host=config.host, port=config.port)
        event_loop.run_coroutine(graphql_client.open())

        global context
        context = Context(graphql_client=graphql_client, event_loop=event_loop, config=config)

        atexit.register(shutdown)
        logger.debug("Aporia SDK initialized.")
    except Exception as err:
        handle_error(
            message="Initializing Aporia SDK failed, error: {}".format(str(err)),
            add_trace=False if debug is None else debug,
            raise_exception=False if throw_errors is None else throw_errors,
            original_exception=err,
        )


def flush(timeout: Optional[int] = None) -> int:
    """Waits for all of the prediction logs to reach the controller.

    Args:
        timeout (int, optional): Maximum number of seconds to wait for the flush to
            complete. Defaults to None (No time limit).

    Returns:
        int: Number of tasks left in the queue after the flush.

    Notes:
        * If the timeout is exceeded, there may be some unfinished tasks left in the queue.
          To make sure that everything is finished, call flush() without timeout.
        * The return value does not include tasks that were added during or
          after the call to flush().
    """
    if context is None:
        logger.error("Flush failed, Aporia SDK was not initialized.")
        return 0

    logger.debug("Flushing remaining data")
    not_done = context.event_loop.flush(timeout=timeout)
    return len(not_done)


def shutdown():
    """Shuts down the Aporia SDK.

    Notes:
        * It is advised to call flush() before calling shutdown(), to ensure that
          all of the data that was sent reaches the controller.
    """
    with suppress(Exception):
        global context
        if context is not None:
            context.event_loop.run_coroutine(context.graphql_client.close())
            context = None
