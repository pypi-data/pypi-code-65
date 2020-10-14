from asyncio import get_event_loop
from typing import Any, Callable, Coroutine, Dict, Union

from nats.aio.client import Client as NATS
from nats.aio.client import Msg as NATSMsg
from nats.aio.client import Subscription as NATSSubscription

from pydantic import BaseModel

from .wrappers.reply import SafeRequestReplyMixin


class ServiceMixin(SafeRequestReplyMixin, object):

    client: NATS
    __service_factories__: Dict[str, Callable]
    subscriptions: Dict[int, NATSSubscription]

    async def __reply__(
        self, subject: str, cb: Callable[[NATSMsg], Coroutine[Any, Any, None]], **kwargs
    ) -> None:
        """Start a request/reply subscription. It supports all options supported by NATS or STAN clients."""
        await self.client.subscribe(
            subject, cb=cb, **kwargs,
        )

    def __service_factory__(
        self,
        subject: str,
        cb: Callable[[BaseModel], None],
        *,
        start: bool = False,
        **kwargs,
    ) -> None:
        """Create and optionally start a new NATS service on given subject using given callback.

        This function is used internally by the reply decorator with decorated function as `cb` argument.
        It performs the following actions:

        - extract message content as bytes
        - parse input data from bytes
        - validate input data
        - execute given function
        - validate output data
        - create new successful ReplyMessage
        - return ReplyMessage serialized into bytes

        Warnings:
            Reply status does not follow POSIX convention and 0 indicates an error.

        Arguments:
            subject: The subject to subscrube to.
            cb: The function to use as callback.
            start: Whether to start the subscription right after definition.
            kwargs: Any argument supported by NATS or STAN subscribe method.
        """
        callback = self._safe_request_reply(cb)

        # Generate a key
        key = f"{subject}_{cb.__name__}"

        # Define a function that will start the subscription
        async def start_service() -> None:
            """Start subscription"""
            await self.__reply__(subject, callback, **kwargs)

        if start:
            loop = get_event_loop()
            loop.run_until_complete(start_service())
        else:
            # Store the function to start the subscription
            self.__service_factories__[key] = start_service

    async def start_services(self) -> None:
        """Start all request/reply services."""
        factory_keys = list(self.__service_factories__.keys())
        while factory_keys:
            key = factory_keys.pop(0)
            start_subscription = self.__service_factories__.pop(key)
            await start_subscription()

    async def stop_services(self) -> None:
        """Stop all request/reply services."""
        sub_ids = list(self.subscriptions.keys())
        while sub_ids:
            sub_id = sub_ids.pop(0)
            subscription = self.subscriptions[sub_id]
            # This works using STAN
            try:
                await subscription.unsubscribe()
            # But raise an AttributeError using NATS
            except AttributeError:
                # In this case we muse unsubscribe through the client
                await self.client.unsubscribe(sub_id)

    def reply(
        self, subject: str, start: bool = False, **kwargs,
    ) -> Callable[[Callable], None]:
        """Create and optionally start a new NATS service on given subject using given callback.

        This function is meant to be used as a decorator.
        
        It ensure that the service will:

        - extract message content as bytes
        - parse input data from bytes
        - validate input data
        - execute given function
        - validate output data
        - create new successful ReplyMessage
        - return ReplyMessage serialized into bytes

        Warnings:
            Reply status does not follow POSIX convention and 0 indicates an error.

        Arguments:
            subject: The subject to subscrube to.
            start: Whether to start the subscription right after definition.
            kwargs: Any argument supported by NATS or STAN subscribe method.

        Examples:
            - Create a request/reply subscription:
        ```python
        from faststan.nats import FastNATS
        from pydantic import BaseModel

        class Message(BaseModel):
            author: str
            content: str

        class Response(BaseModel):
            greeting: str

        app = FastNATS()

        @app.reply("demo")
        def on_message(message: Message) -> Response:
            return Response(greeting=f"Hello {message.author}")

        response = await app.request_json({"author": "John", "content": "Hello!"})

        Response(**response.value)
        ```
        """

        def decorator(function: Callable) -> None:
            """Register a new subscriber

            Arguments:
                function: The function that will be used as callback when receiving messages.
            """
            return self.__service_factory__(subject, function, **kwargs)

        # We must return the decorator else python complains but it will never be used
        return decorator
