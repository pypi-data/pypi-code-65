import json
import logging
from typing import Any, Callable
import os

import pulsar

from . import Engine

LOGGER = logging.getLogger(__name__)

ENV_PULSAR_CONNECTION = "PULSAR_CONNECTION"
DEFAULT_PULSAR_CONNECTION = "pulsar://localhost:6650"

ENV_TOPIC = "PULSAR_TOPIC"
ENV_SUBSCRIPTION = "PULSAR_SUBSCRIPTION"

ENV_DECODER = "PULSAR_DECODER"
DEFAULT_DECODER = "identity"

TIMEOUT = 60000


def identity_decoder(raw):
    return raw.decode("utf-8")


def json_decoder(raw):
    return json.loads(raw)


def create_decoder_from_env():
    decoder = os.environ.get(ENV_DECODER, DEFAULT_DECODER)
    if decoder == "json":
        decoder = json_decoder
    else:
        decoder = identity_decoder
    return decoder


class PulsarPubSub(Engine):
    """Synchronous engine based on apache pulsar"""

    def __init__(
        self,
        service_url: str,
        topic: str,
        subscription: str,
        *,
        decoder: Callable[[bytes], Any] = lambda x: x,
    ):
        self.client = pulsar.Client(service_url)
        self.consumer = self.client.subscribe(
            topic,
            subscription,
            consumer_type=pulsar.ConsumerType.Shared,
            receiver_queue_size=10,
        )
        self.decoder = decoder

    @classmethod
    def from_env(cls):
        service_url = os.environ.get(ENV_PULSAR_CONNECTION, DEFAULT_PULSAR_CONNECTION)
        topic = os.environ.get(ENV_TOPIC, None)
        if topic is None:
            raise ValueError(f"{ENV_TOPIC} must be set")

        subscription = os.environ.get(ENV_SUBSCRIPTION, None)
        if subscription is None:
            raise ValueError(f"{ENV_SUBSCRIPTION} must be set")

        decoder = create_decoder_from_env()
        return cls(service_url, topic, subscription, decoder=decoder)

    def next(self):
        # TODO(msimonin): handle error here
        msg = self.consumer.receive(timeout_millis=TIMEOUT)
        self.current_msg = msg
        return self.decoder(msg.data())

    def ack(self, param):
        self.consumer.acknowledge(self.current_msg)

    def nack(self, param):
        self.consumer.negative_acknowledge(self.current_msg)
