import json
from queue import Queue
from typing import Dict, Any

from pika.exceptions import StreamLostError
from twisted.internet import reactor

from agent.rabbitmq.client import RabbitMqClient

publish_message_queue = Queue()


class RabbitMQPublisher:
    def __init__(self):
        self.client = RabbitMqClient()
        self.logger = self.client.logger
        self._is_publishing_active = False

    def start_publishing_messages(self):
        self.logger.info("Starting publishing messages to RabbitMQ")
        self._is_publishing_active = True
        reactor.callInThread(self._run)

    def stop_publishing_messages(self):
        if self._is_publishing_active and publish_message_queue.empty():
            self.logger.info("Stopping publishing messages to RabbitMQ")
            publish_message_queue.put(None)

    def _run(self) -> None:
        while True:
            message = publish_message_queue.get()
            if message is None:
                self.logger.info("None in publish_message_queue")
                break
            try:
                self.publish_message(message)
            except StreamLostError:
                publish_message_queue.put(message)
        self._is_publishing_active = False

    def publish_message(self, message: Dict[str, Any]) -> None:
        rabbitmq_message = json.dumps(message).encode("utf-8")
        self.client.publish_message(
            message=rabbitmq_message,
            message_type=message["messageType"],
            topic=message["nodeServiceId"],
        )
