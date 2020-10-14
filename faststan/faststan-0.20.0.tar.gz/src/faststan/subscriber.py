from asyncio import get_event_loop
from typing import Any, Callable, Coroutine, Dict, Union

from nats.aio.client import Client as NATS
from nats.aio.client import Subscription as NATSSubscription
from nats.aio.client import Msg as NATSMsg
from stan.aio.client import Client as STAN
from stan.aio.client import Subscription as STANSubscription
from stan.aio.client import Msg as STANMsg
from pydantic import BaseModel

from .wrappers.subscribe import SafeSubscribeMixin, DEFAULT_ERROR_CB


class SubscriberMixin(SafeSubscribeMixin, object):

    client: Union[NATS, STAN]
    subscriptions: Dict[Union[int, str], Union[STANSubscription, NATSSubscription]]
    __subscription_factories__: Dict[str, Callable]

    async def __subscribe__(
        self,
        subject: str,
        cb: Callable[
            [Union[STANSubscription, NATSSubscription]], Coroutine[Any, Any, None]
        ],
        **kwargs,
    ) -> None:
        """Start a subscription. It supports all options supported by NATS or STAN clients."""
        await self.client.subscribe(
            subject, cb=cb, **kwargs,
        )

    def __subscription_factory__(
        self,
        subject: str,
        cb: Callable[[BaseModel], Any],
        error_cb: Callable[[Exception, Union[NATSMsg, STANMsg]], None],
        *,
        start: bool = False,
        **kwargs,
    ) -> None:
        callback = self._safe_subscribe(cb, error_cb)

        # Generate a key
        key = f"{subject}_{cb.__name__}"

        # Define a function that will start the subscription
        async def start_subscription() -> Any:
            """Start subscription"""
            await self.__subscribe__(subject, callback, **kwargs)

        if start:
            loop = get_event_loop()
            loop.run_until_complete(start_subscription())
        else:
            # Store the function to start the subscription
            self.__subscription_factories__[key] = start_subscription

    async def start_subscriptions(self) -> None:
        """Start all subscriptions."""
        factory_keys = list(self.__subscription_factories__.keys())
        while factory_keys:
            key = factory_keys.pop(0)
            start_subscription = self.__subscription_factories__.pop(key)
            await start_subscription()

    async def stop_subscriptions(self) -> None:
        """Stop all subcriptions."""
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

    def subscribe(
        self,
        subject: str,
        error_cb: Callable[
            [Exception, Union[NATSMsg, STANMsg]], None
        ] = DEFAULT_ERROR_CB,
        **kwargs,
    ) -> Callable[[Callable], None]:
        """Register a new subscriber.

        Warning: This does not start the subcription.

        Arguments:
            subject: The subject (channel) to subscribe to.
            error_cb: The function that handles errors.
            **kwargs: Any valid keyword argument for the stan client `.subscribe()` method.
        """

        def decorator(function: Callable) -> None:
            """Register a new subscriber

            Arguments:
                function: The function that will be used as callback when receiving messages.
            """
            return self.__subscription_factory__(subject, function, error_cb, **kwargs)

        # We must return the decorator else python complains but it will never be used
        return decorator
