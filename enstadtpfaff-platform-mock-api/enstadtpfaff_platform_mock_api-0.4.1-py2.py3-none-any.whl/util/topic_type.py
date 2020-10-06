from enum import Enum

from .constants import SHARED_TOPIC, SERVICE_TOPIC


class TopicType(Enum):
    SHARED = SHARED_TOPIC
    SERVICE_SPECIFIC = SERVICE_TOPIC
