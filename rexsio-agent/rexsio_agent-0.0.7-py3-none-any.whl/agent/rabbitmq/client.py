import time

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import IncompatibleProtocolError

from agent.config.properties import RABBITMQ_URL
from agent.logger import get_logger


class RabbitMqClient:
    EXCHANGE = "agent"
    EXCHANGE_TYPE = "topic"

    def __init__(self):
        self._parameters = pika.URLParameters(RABBITMQ_URL)
        self._connection = None
        self._channel = None
        self._exchange_declared = False
        self.logger = get_logger("rabbitmq")
        self.declared_queues = []

    @property
    def channel(self) -> BlockingChannel:
        if self._connection is None:
            self._connect()

        if self._channel is None or not self._channel.is_open:
            self.logger.info("Trying to reconnect RabbitMQ...")
            self._connect()

        return self._channel

    def publish_message(self, message: bytes, message_type: str, topic: str) -> None:
        if topic not in self.declared_queues:
            self.declare_queue(topic)

        self.channel.basic_publish(
            exchange=self.EXCHANGE,
            routing_key=topic,
            body=message,
            properties=pika.BasicProperties(
                content_type="application/json", type=message_type
            ),
        )
        self.logger.info(f"Message sent to RabbitMQ: {message}")

    def consume_message(self, queue_name):
        return self.channel.basic_get(queue_name)

    def declare_queue(self, routing_key: str) -> None:
        self.channel.queue_declare(queue=routing_key)
        self.channel.queue_bind(
            exchange=self.EXCHANGE, queue=routing_key, routing_key=routing_key
        )
        self.declared_queues.append(routing_key)
        self.logger.info(f"Declared queue with topic: {routing_key}")

    def basic_ack(self, ack):
        return self.channel.basic_ack(ack)

    def basic_nack(self, nack):
        return self.channel.basic_nack(nack)

    def _connect(self):
        self.logger.info(f"Creating connection with parameters {self._parameters}")
        self._connection = self._wait_for_connection()
        self._channel = self._connection.channel()

        if not self._exchange_declared:
            self._declare_exchange()

    def _wait_for_connection(self):
        while True:
            try:
                return pika.BlockingConnection(self._parameters)
            except IncompatibleProtocolError:
                self.logger.exception(
                    "Cannot establish connection with RabbitMQ. Trying to reconnect..."
                )
                time.sleep(3)

    def _declare_exchange(self):
        self.logger.info("Declare exchange")
        self.channel.exchange_declare(
            exchange=self.EXCHANGE, exchange_type=self.EXCHANGE_TYPE
        )
        self._exchange_declared = True
