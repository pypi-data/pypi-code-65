from typing import Optional, Callable

from .event import Event
from .event_broker import EventBroker
from .platform_mock_api import PlatformMockApi


def connect(
        mqtt_address: str,
        mqtt_username: str,
        mqtt_password: str,
        sender_name: str,
        event_handler: Optional[Callable[[Event], None]] = None
) -> PlatformMockApi:
    if mqtt_address is None or len(mqtt_address) == 0:
        raise ValueError("mqtt_address must not be blank")
    if mqtt_username is None or len(mqtt_address) == 0:
        raise ValueError("mqtt_username must not be blank")
    if mqtt_password is None or len(mqtt_address) == 0:
        raise ValueError("mqtt_password must not be blank")
    if sender_name is None or len(mqtt_address) == 0:
        raise ValueError("sender_name must not be blank")

    import uuid
    client_id = sender_name + ":" + str(uuid.uuid4())
    event_broker = EventBroker(
        mqtt_address=mqtt_address,
        mqtt_username=mqtt_username,
        mqtt_password=mqtt_password,
        client_id=client_id,
        event_handler=event_handler
    )
    platform_mock_api = PlatformMockApi(event_broker, sender_name)
    return platform_mock_api
