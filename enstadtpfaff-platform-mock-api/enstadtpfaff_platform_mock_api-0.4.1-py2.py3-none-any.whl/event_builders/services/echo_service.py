from enstadtpfaff_platform_mock_api.event import Event
from enstadtpfaff_platform_mock_api.util.topic_util import name_for_service_specific_topic


class EchoServiceEventBuilder:
    SERVICE_ID = 'pm-echo-service'
    PING_TOPIC = name_for_service_specific_topic(SERVICE_ID, 'ping')

    @staticmethod
    def ping(payload: str) -> Event:
        return Event(EchoServiceEventBuilder.PING_TOPIC, payload)
