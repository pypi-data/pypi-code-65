from typing import Dict

from stan.aio.client import Client as STAN
from stan.aio.client import Msg as STANMsg
from stan.aio.client import Subscription as STANSubscription

from .publisher import PublisherMixin
from .subscriber import SubscriberMixin
from .settings import FastSTANSettings
from .nats import FastNATS


class FastSTAN(PublisherMixin, SubscriberMixin, object):
    def __init__(self, settings: FastSTANSettings = None) -> None:
        """Return a new FastSTAN instance."""
        # Validate settings
        if settings is None:
            self.settings = FastSTANSettings()
        elif isinstance(settings, FastSTANSettings):
            self.settings = settings
        else:
            self.settings = FastSTANSettings(**settings)
        # Initialize NATS client
        self.nats = FastNATS(self.settings.nats)
        self.client = STAN()
        # Initialize factories
        self.__subscription_factories__ = {}

    @property
    def is_connected(self) -> bool:
        """Return True if client is connected to NATS server else false."""
        return self.nats.is_connected

    @property
    def subscriptions(self) -> Dict[str, STANSubscription]:
        """Return dictionnary of subscriptions."""
        return self.client._sub_map

    async def connect(self) -> None:
        """Connect NATS streaming on top of NATS cluster"""
        await self.nats.connect()
        # client on top.
        await self.client.connect(
            self.settings.stan.cluster, self.settings.stan.client, nats=self.nats.client
        )

    async def close(self) -> None:
        await self.client.close()
        await self.nats.close()

    async def start(self) -> None:
        """Start subscriptions."""
        await self.start_subscriptions()

    async def stop(self) -> None:
        """Stop subscriptions."""
        await self.stop_subscriptions()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"host={self.settings.nats.host}, port={self.settings.nats.port}, "
            f"client={self.client}, client_name={self.settings.stan.client}, "
            f"cluster={self.settings.stan.cluster})"
        )

    async def __aenter__(self) -> "FastSTAN":
        await self.connect()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.stop()
        await self.close()
