
import paho.mqtt.client as mqtt
from spce import CloudEvent, Json

from .source import EventSource


class Mqtt:

    def __init__(self, host: str, port: int, topic = ""):
        self.host = host
        self.port = port
        self.topic = topic
        self.mqtt_client = mqtt.Client()
        # client.on_connect
        # client.on_message
        self.mqtt_client.connect(host=host, port=port)

    def event_source(self, topic: str, *,
                     type="",
                     source="",
                     datacontenttype="application/json",
                     dataschema="",
                     subject="") -> EventSource:
        client = Mqtt(self.host, self.port, topic)
        return EventSource(client,
                           type=type,
                           source=source,
                           datacontenttype=datacontenttype,
                           dataschema=dataschema,
                           subject=subject)

    def post_event(self, event: CloudEvent, topic = "", *, qos=0):
        topic = topic or self.topic
        # TODO: content type from /v0/info
        payload = Json.encode(event)
        return self.mqtt_client.publish(topic, payload, qos=qos)
