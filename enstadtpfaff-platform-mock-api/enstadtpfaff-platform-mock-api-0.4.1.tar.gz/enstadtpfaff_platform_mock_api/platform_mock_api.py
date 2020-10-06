from .event import Event
from .event_broker import EventBroker
from .event_builders.shared.platform_events import PlatformEventsEventBuilder


class PlatformMockApi:
    def __init__(self,
                 event_broker: EventBroker,
                 sender_name: str
                 ):
        self._event_broker = event_broker
        self._sender_name = sender_name

    @property
    def event_broker(self) -> EventBroker:
        return self._event_broker

    @property
    def sender_name(self):
        return self._sender_name

    def create_hello_platform_event(self, description: str) -> Event:
        return PlatformEventsEventBuilder.hello_platform(self.sender_name, description)

    def create_goodbye_platform_event(self) -> Event:
        return PlatformEventsEventBuilder.goodbye_platform(self.sender_name)

    def create_alive_ping_event(self) -> Event:
        return PlatformEventsEventBuilder.alive_ping(self.sender_name)
