from asyncio import iscoroutinefunction
from typing import (
    Any,
    Callable,
    Coroutine,
    List,
    Optional,
    Tuple,
    Type,
    Dict,
    Union,
)

from nats.aio.client import Client as NATS
from nats.aio.client import Msg as NATSMsg
from stan.aio.client import Client as STAN
from stan.aio.client import Msg as STANMsg

from pydantic import BaseModel

from returns.future import future_safe
from returns.pipeline import flow, pipe, is_successful
from returns.pointfree import bind

from loguru import logger

from ..inspect import inspect_subscription_callback, inspect_extra_params
from ..utils import always_run_async


def DEFAULT_ERROR_CB(error: Exception, msg: Union[NATSMsg, STANMsg]) -> None:
    try:
        subject = msg.subject
    except AttributeError:
        subject = msg.sub.subject
    logger.error(
        f"Error encoutered on subject '{subject}'. Message: {msg}. Error details: {error}"
    )


class SafeSubscribeMixin:

    client: NATS

    def _safe_subscribe(
        self,
        function: Callable[..., None],
        error_callback: Callable[
            [Exception, Union[NATSMsg, STANMsg]], Any
        ] = DEFAULT_ERROR_CB,
    ) -> Callable[[NATSMsg], Coroutine[Any, Any, None]]:
        """Return a new function that will:

        - extract content as bytes from message
        - parse input data from bytes
        - validate input data
        - execute given function
        - acknowledge message

        If any exception is raised during one of those steps, the error callback will be executed with
        the message and the exception raised as arguments.

        Warnings:

            Do not forget to acknowledge the messages !

        Arguments:

            function: The function to execute on validated data.
            error_callback: The function to call on error.

        Returns:

            None.
        """
        input_model, _, extra_params = inspect_subscription_callback(
            function, allow_no_return=True
        )

        (
            include_message,
            message_param,
            include_subject,
            subject_param,
        ) = inspect_extra_params(extra_params)

        async def inject_kwargs(msg: Union[NATSMsg, STANMsg]) -> Dict[str, Any]:
            additional_kwargs = {}
            # Inject message if needed
            if include_message:
                additional_kwargs[message_param] = msg
            # Inject subject if needed
            if include_subject:
                additional_kwargs[subject_param] = msg.subject
            return additional_kwargs

        async def validate_message(data: bytes) -> BaseModel:
            """Validate data based on pydantic model."""
            logger.debug("Received data: {!r}".format(data))
            return input_model.parse_raw(data)

        async def execute_function(data: BaseModel, **kwargs) -> None:
            """Execute user defined callback."""
            await always_run_async(function, data, **kwargs)

        def gather_error(error: Exception) -> Exception:
            """Gather error into ReplyMessage."""
            logger.debug(f"Gathering exception: {error}")
            return error

        @future_safe
        async def __future_process_message__(msg: Union[NATSMsg, STANMsg]) -> None:
            """Process message in a request/reply pattern."""
            # Validate input data
            data = await validate_message(msg.data)
            # Construct optional keyword arguments
            kwargs = await inject_kwargs(msg)
            # Compute result in a future
            await execute_function(data, **kwargs)

        async def safe_subscribe(msg: Union[NATSMsg, STANMsg]) -> None:
            """Process message in a request/reply pattern"""

            result = await __future_process_message__(msg)
            if not is_successful(result):
                await always_run_async(error_callback, result.rescue(gather_error), msg)

            await self.client.ack(msg)

        return safe_subscribe
