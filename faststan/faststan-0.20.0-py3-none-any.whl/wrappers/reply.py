from asyncio import iscoroutinefunction
from typing import Any, Callable, Coroutine, Dict, Type, Union

from nats.aio.client import Client as NATS
from nats.aio.client import Msg as NATSMsg

from pydantic import BaseModel

from returns.future import future_safe
from returns.pipeline import flow, pipe, is_successful
from returns.pointfree import bind

from loguru import logger

from ..inspect import inspect_subscription_callback, inspect_extra_params
from ..models import ReplyStatus, ReplyMessage
from ..utils import always_run_async


class SafeRequestReplyMixin:

    client: NATS

    def _safe_request_reply(
        self, function: Callable[..., BaseModel]
    ) -> Callable[[NATSMsg], Coroutine[Any, Any, None]]:
        """Return a new function that will:

        - parse input data from bytes
        - validate input data
        - execute given function
        - validate output data
        - create new successful ReplyMessage
        - return ReplyMessage serialized into bytes

        If any exception is raised during one of those steps, a failed ReplyMessage holding exception as string
        will be created and serialized into bytes.

        Warnings:
        -----------
            Reply status does not follow POSIX convention and 0 indicates an error.

        Arguments:
        -----------
            function: The function to execute on validated data.

        Returns:
        -----------
            A ReplyMessage with status either 1 (ReplyStatus.SUCCESS) or 0 (ReplyStatus.FAILURE) and optionally a value or an error.
        """
        input_model, output_model, extra_params = inspect_subscription_callback(
            function
        )

        (
            include_message,
            message_param,
            include_subject,
            subject_param,
        ) = inspect_extra_params(extra_params)

        async def inject_kwargs(msg: NATSMsg) -> Dict[str, Any]:
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

        async def execute_function(data: BaseModel, **kwargs) -> BaseModel:
            """Execute user defined callback."""
            return await always_run_async(function, data, **kwargs)

        async def gather_result(result: BaseModel) -> ReplyMessage:
            """Gather result into ReplyMessage."""
            logger.debug(f"Gathering result: {result}")
            reply_msg = ReplyMessage(
                status=ReplyStatus.SUCCESS, result=result, error=None
            )
            logger.debug(f"Generate reply message: {reply_msg}")
            return reply_msg

        async def serialize_reply(message: ReplyMessage) -> bytes:
            """Serialize ReplyMessage into bytes."""
            return bytes(message.json(), "utf-8")

        def gather_error(error: Exception) -> ReplyMessage:
            """Gather error into ReplyMessage."""
            logger.debug(f"Gathering exception: {error}")
            reply_msg = ReplyMessage(
                status=ReplyStatus.FAILURE, result=None, error=str(error)
            )
            logger.debug(f"Generate reply message: {reply_msg}")
            return reply_msg

        @future_safe
        async def __future_process_message__(msg: NATSMsg) -> bytes:
            """Process message in a request/reply pattern."""
            # Validate input data
            data = await validate_message(msg.data)
            # Construct optional keyword arguments
            kwargs = await inject_kwargs(msg)
            # Compute result in a future
            result = await execute_function(data, **kwargs)
            # Gather ReplyMessage from future
            reply_msg = await gather_result(result)
            # Serialize ReplyMessage into bytes
            reply_bytes = await serialize_reply(reply_msg)
            # Return reply
            return reply_bytes

        async def safe_request_reply(msg: NATSMsg) -> None:
            """Process message in a request/reply pattern"""

            result = await __future_process_message__(msg)
            if is_successful(result):
                reply_bytes = result.bind(lambda x: x)
            else:
                reply_bytes = bytes(result.rescue(gather_error).json(), "utf-8")
            # When do we want to do this ?
            if not msg.reply:
                await self.client.ack(msg)
                # Maybe at the top of this function
                return
            logger.debug(f"Replying with message: {reply_bytes}")
            await self.client.publish(msg.reply, reply_bytes)
            await self.client.ack(msg)

        return safe_request_reply
