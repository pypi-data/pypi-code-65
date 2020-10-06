import functools
import threading
import time

import pika

from agent.config.properties import RABBITMQ_URL
from agent.constants import NOTIFY_CONTROL_CENTER, EXCHANGE, EXCHANGE_TYPE
from agent.rabbitmq import logger


class RabbitMqClient(object):
    def __init__(self):
        self.should_reconnect = False
        self.was_consuming = False
        self.should_stop = False

        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = RABBITMQ_URL
        self._consuming = False
        self._prefetch_count = 1

    def connect(self):
        logger.info(f"Connecting to {self._url}")
        return pika.SelectConnection(
            parameters=pika.URLParameters(self._url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed,
        )

    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            logger.info("Connection is closing or already closed")
        else:
            logger.info("Closing connection")
            self._connection.close()

    def on_connection_open(self, _unused_connection):
        logger.info("Connection opened")
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        logger.error(f"Connection open failed: {err}")
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logger.warning(f"Connection closed, reconnect necessary: {reason}")
            self.reconnect()

    def reconnect(self):
        self.should_reconnect = True
        self.stop()

    def open_channel(self):
        logger.info("Creating a new channel")
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        logger.info("Channel opened")
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(EXCHANGE)

    def add_on_channel_close_callback(self):
        logger.info("Adding channel close callback")
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        logger.warning(f"Channel {channel} was closed: {reason}")
        self.close_connection()

    def setup_exchange(self, exchange_name):
        logger.info(f"Declaring exchange: {exchange_name}")
        cb = functools.partial(self.on_exchange_declareok, userdata=exchange_name)
        self._channel.exchange_declare(
            exchange=exchange_name, exchange_type=EXCHANGE_TYPE, callback=cb
        )

    def on_exchange_declareok(self, _unused_frame, userdata):
        logger.info(f"Exchange declared: {userdata}")
        self.setup_queue(NOTIFY_CONTROL_CENTER)

    def setup_queue(self, queue_name):
        logger.info(f"Declaring queue {queue_name}")
        cb = functools.partial(self.on_queue_declareok, userdata=queue_name)
        self._channel.queue_declare(queue=queue_name, callback=cb)

    def on_queue_declareok(self, _unused_frame, userdata):
        queue_name = userdata
        logger.info(f"Binding {EXCHANGE} to {queue_name} with {NOTIFY_CONTROL_CENTER}")
        cb = functools.partial(self.on_bindok, userdata=queue_name)
        self._channel.queue_bind(
            queue_name, EXCHANGE, routing_key=NOTIFY_CONTROL_CENTER, callback=cb
        )

    def on_bindok(self, _unused_frame, userdata):
        logger.info(f"Queue bound: {userdata}")
        self.set_qos()

    def set_qos(self):
        self._channel.basic_qos(
            prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok
        )

    def on_basic_qos_ok(self, _unused_frame):
        logger.info(f"QOS set to: {self._prefetch_count}")
        self.start_consuming()

    def start_consuming(self):
        logger.info("Issuing consumer related RPC commands")
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(
            NOTIFY_CONTROL_CENTER, self.on_message
        )
        self.was_consuming = True
        self._consuming = True

    def add_on_cancel_callback(self):
        logger.info("Adding consumer cancellation callback")
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        logger.info(f"Consumer was cancelled remotely, shutting down: {method_frame}")
        if self._channel:
            self._channel.close()

    def on_message(self, _unused_channel, basic_deliver, _properties, body):
        logger.info(f"Received message # {basic_deliver.delivery_tag}: {body}")
        self.notify_control_center(body)
        self.acknowledge_message(basic_deliver.delivery_tag)

    @staticmethod
    def notify_control_center(body: bytes) -> None:
        from agent.websocket.client import AgentWebSocketClient

        AgentWebSocketClient.get_instance().safe_message_send(body)

    def acknowledge_message(self, delivery_tag):
        logger.info(f"Acknowledging message {delivery_tag}")
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        if self._channel:
            logger.info("Sending a Basic.Cancel RPC command to RabbitMQ")
            cb = functools.partial(self.on_cancelok, userdata=self._consumer_tag)
            self._channel.basic_cancel(self._consumer_tag, cb)

    def on_cancelok(self, _unused_frame, userdata):
        self._consuming = False
        logger.info(
            f"RabbitMQ acknowledged the cancellation of the consumer: {userdata}"
        )
        self.close_channel()

    def close_channel(self):
        logger.info("Closing the channel")
        self._channel.close()

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        if not self._closing:
            self._closing = True
            logger.info("Stopping")
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            logger.info("Stopped")

    def publish_message(self, message: bytes, message_type: str, topic: str) -> None:
        self._channel.queue_bind(exchange=EXCHANGE, queue=topic, routing_key=topic)
        self._channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=topic,
            body=message,
            properties=pika.BasicProperties(
                content_type="application/json", type=message_type
            ),
        )


class ReconnectingRabbitMqClient(object):
    _instance = None

    @staticmethod
    def get_instance():
        if ReconnectingRabbitMqClient._instance is None:
            ReconnectingRabbitMqClient._instance = ReconnectingRabbitMqClient()
        return ReconnectingRabbitMqClient._instance

    def __init__(self):
        self._reconnect_delay = 0
        self._stop_consuming_event = threading.Event()
        self.client = RabbitMqClient()
        self.thread = None

    def start_consuming_messages(self):
        logger.info("Starting consuming messages on RabbitMQ")
        self.thread = threading.Thread(
            target=self._run, args=(self._stop_consuming_event,)
        )
        self.thread.start()

    def stop_consuming_messages(self):
        logger.info("Stopping consuming messages on RabbitMQ")
        self._stop_consuming_event.set()
        self.client.stop_consuming()
        self.thread.join()

    def _run(self, stop_event: threading.Event) -> None:
        while not stop_event.isSet():
            self.client.run()
            self._maybe_reconnect()

    def _maybe_reconnect(self):
        if self.client.should_reconnect:
            self.client.stop()
            reconnect_delay = self._get_reconnect_delay()
            logger.info(f"Reconnecting after {reconnect_delay} seconds")
            time.sleep(reconnect_delay)
            self.client = RabbitMqClient()

    def _get_reconnect_delay(self):
        if self.client.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay
