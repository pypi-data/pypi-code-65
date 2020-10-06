from enstadtpfaff_platform_mock_api.event import Event
from enstadtpfaff_platform_mock_api.util.topic_util import name_for_shared_topic


class PlatformEventsEventBuilder:
    SHARED_TOPIC_ID = "platform-events"
    HELLO_PLATFORM_TOPIC = name_for_shared_topic(SHARED_TOPIC_ID, "hello-platform")
    GOODBYE_PLATFORM_TOPIC = name_for_shared_topic(SHARED_TOPIC_ID, "goodbye-platform")
    ALIVE_PING_TOPIC = name_for_shared_topic(SHARED_TOPIC_ID, "alive-ping")

    @staticmethod
    def hello_platform(name: str, description: str) -> Event:
        return Event(
            topic=PlatformEventsEventBuilder.HELLO_PLATFORM_TOPIC,
            payload={
                'name': name,
                'description': description
            }
        )

    @staticmethod
    def goodbye_platform(name: str) -> Event:
        return Event(
            topic=PlatformEventsEventBuilder.GOODBYE_PLATFORM_TOPIC,
            payload={
                'name': name
            }
        )

    @staticmethod
    def alive_ping(name: str) -> Event:
        return Event(
            topic=PlatformEventsEventBuilder.ALIVE_PING_TOPIC,
            payload={
                'name': name
            }
        )
