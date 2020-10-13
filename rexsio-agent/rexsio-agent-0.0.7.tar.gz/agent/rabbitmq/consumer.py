import time
from queue import Queue
from threading import Event

from twisted.internet import reactor

from agent.rabbitmq.client import RabbitMqClient

notify_control_center_queue = Queue()


class RabbitMqConsumer(object):
    QUEUE_NAME = "NOTIFY_CONTROL_CENTER"

    def __init__(self):
        self.client = RabbitMqClient()
        self.logger = self.client.logger
        self._stop_consuming_event = Event()
        self._interval = 0.1

    def start_consuming_messages(self):
        self.logger.info("Starting consuming messages from RabbitMQ")
        self.client.declare_queue(self.QUEUE_NAME)
        self._stop_consuming_event.clear()
        reactor.callInThread(self._run, self._stop_consuming_event)

    def stop_consuming_messages(self):
        if not self._stop_consuming_event.isSet():
            self.logger.info("Stopping consuming messages from RabbitMQ")
            self._stop_consuming_event.set()

    def _run(self, stop_event: Event) -> None:
        while not stop_event.isSet():
            frame, _, body = self.client.consume_message(self.QUEUE_NAME)

            if frame and body:
                ack_tag = frame.delivery_tag
                notify_control_center_queue.put(body)
                self.client.basic_ack(ack_tag)

            time.sleep(self._interval)
