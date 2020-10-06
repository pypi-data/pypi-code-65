import json


class Event:
    def __init__(self, topic: str, payload):
        self._topic: str = topic
        if isinstance(payload, str):
            self._payload: str = payload
        else:
            self._payload: str = json.dumps(payload)

    def __str__(self):
        return "Event{" + \
               "topic='" + self.topic + '\'' + \
               ", payload='" + self.payload + '\'' + \
               '}'

    @property
    def topic(self) -> str:
        return self._topic

    @property
    def payload(self) -> str:
        return self._payload
