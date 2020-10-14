from typing import Dict, Optional, Union, Mapping

from nats.aio.client import Client as NATS
from nats.aio.client import Msg as NATSMsg
from nats.aio.client import Subscription as NATSSubscription

from .settings import NATSClientSettings
from .publisher import PublisherMixin
from .subscriber import SubscriberMixin
from .service import ServiceMixin


class FastNATS(ServiceMixin, SubscriberMixin, PublisherMixin, object):
    """Easy to use NATS client.

    This class can be use to create subscriptions or publish messages.
    It uses the official library client from nats.aio.client under the hood and let users declare
    subscriptions using decorators, while automating serialization/deserialization using pydantic library.

    Arguments:
        settings: Either a dictionnary of settings or an instance of NATSClientSettings.
        kwargs: Any keyword argument supported by nats.aio.client.Client.


    Examples:
        - Create a simple subscription:
    ```python
    app = FastNATS()

    class Event(BaseModel):
        title: str
        timestamp: int

    @app.subscribe("events")
    def on_event(event: Event):
        print(f"Received new event: {event.json()}")

    await app.connect()
    await app.start()

    await app.publish_json("events", {"title": "Test event", "timestamp": 123456789})
    ```
    """

    def __init__(
        self, settings: Optional[Union[NATSClientSettings, Mapping]] = None, **kwargs
    ) -> None:
        """Return a new FastSTAN instance.

        Arguments:
            settings: Either a dictionnary of settings or an instance of NATSClientSettings.
        """
        # Validate settings
        if settings is None:
            self.settings = NATSClientSettings()
        elif isinstance(settings, NATSClientSettings):
            self.settings = settings
        else:
            self.settings = NATSClientSettings(**settings)
        # Initialize NATS client
        self.client = NATS(**kwargs)
        # Initialize factories
        self.__service_factories__ = {}
        self.__subscription_factories__ = {}

    @property
    def is_connected(self) -> bool:
        """Return True if client is connected to NATS server else false."""
        return self.client.is_connected

    @property
    def subscriptions(self) -> Dict[int, NATSSubscription]:
        """Return a readonly dictionnary holding all active subscriptions."""
        return self.client._subs

    async def connect(self) -> None:
        """Connect to NATS cluster with default timeout.

        Todos:
            - Allow user to specify custom timeout.
        """
        # client on top.
        await self.client.connect([f"nats://{self.settings.host}:{self.settings.port}"])

    async def start(self) -> None:
        """Start subscriptions and services.

        Notes:
            - This does not connect the client to NATS cluster. The clienst must be ALREADY connected to start subscriptions.
        """
        await self.start_services()
        await self.start_subscriptions()

    async def stop(self) -> None:
        """Stop subscriptions and services.

        Notes:
            - This does not disconnect the client from NATS cluster. The clienst must be disconnected AFTER shuting down subscriptions.
        """
        await self.stop_services()
        await self.stop_subscriptions()

    async def close(self) -> None:
        """Close NATS connection."""
        await self.client.close()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.settings.host}, port={self.settings.port}, client={self.client})"

    async def __aenter__(self) -> "FastNATS":
        await self.connect()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.stop()
        await self.close()
