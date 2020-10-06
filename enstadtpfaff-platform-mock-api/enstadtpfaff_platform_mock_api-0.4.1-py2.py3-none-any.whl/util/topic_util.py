from .constants import TOPIC_LEVEL_SEPARATOR, TOPIC_ROOT
from .topic_type import TopicType


def _combine_topic_paths(*path_segments: str) -> str:
    return TOPIC_LEVEL_SEPARATOR.join(path_segments)


def _typed_topic(topic_type: TopicType, topic_id: str, *additional_segments: str):
    return _combine_topic_paths(*[TOPIC_ROOT, topic_type.value, topic_id, *additional_segments])


def name_for_shared_topic(shared_topic_id: str, *additional_segments: str):
    return _typed_topic(TopicType.SHARED, shared_topic_id, *additional_segments)


def name_for_service_specific_topic(service_id: str, *additional_segments: str):
    return _typed_topic(TopicType.SERVICE_SPECIFIC, service_id, *additional_segments)
