import asyncio
import json
from typing import Any, Union
from dataclasses import is_dataclass, asdict

import confluent_kafka
from threading import Thread

from plain_kafka.logger import LOGGER


def _encode_msg(msg) -> Union[str, bytes]:
    """Returns bytes msg if receive bytes, else try to serialise obj to str for comfort reading value in kafka topics"""
    if isinstance(msg, str) or isinstance(msg, bytes):
        return msg
    # if msg is tass entity
    elif hasattr(msg, 'make_dump'):
        encoded_msg = json.dumps(msg.make_dump(), default=str)
    elif is_dataclass(msg):
        encoded_msg = json.dumps(asdict(msg), default=str)
    elif isinstance(msg, dict):
        encoded_msg = json.dumps(msg, default=str)
    else:
        raise TypeError('message for kafka must be dict, str, or dataclass, got {}'.format(type(msg)))
    return encoded_msg


class AsyncProducer:
    def __init__(self, configs: dict):
        self._loop = asyncio.get_event_loop()
        self._producer = confluent_kafka.Producer(configs)
        self._cancelled = False
        self._poll_thread = Thread(target=self._poll_loop)
        self._poll_thread.start()

    def _poll_loop(self):
        while not self._cancelled:
            self._producer.poll(0.1)

    def close(self):
        self._cancelled = True
        self._poll_thread.join()

    # todo add for value valid types (dataclass, marshmallow dataclass)
    def produce(self, topic: str, value: Any, error: str = None):
        """
        An awaitable produce method.

        :param topic: kafka topic
        :param value: msg value
        :param error: usually use for worker if handling msg failed
        :return: confluent_kafka.Message
        """
        result = self._loop.create_future()
        value = _encode_msg(value)

        def ack(err, msg):
            if err:
                self._loop.call_soon_threadsafe(result.set_exception, confluent_kafka.KafkaException(err))
                LOGGER.error('Failed producing msg {} with err: {}'.format(msg, err))
            else:
                self._loop.call_soon_threadsafe(result.set_result, msg)
        self._producer.produce(topic, value, on_delivery=ack, headers=dict(error=error))
        return result


class Producer:
    def __init__(self, configs):
        self._producer = confluent_kafka.Producer(configs)
        self._cancelled = False
        self._poll_thread = Thread(target=self._poll_loop)
        self._poll_thread.start()

    def _poll_loop(self):
        while not self._cancelled:
            self._producer.poll(0.1)

    def close(self):
        self._cancelled = True
        self._poll_thread.join()

    def produce(self, topic: str, value: Any, error: str = None, on_delivery=None):
        """
        :param topic: kafka topic
        :param value: msg value
        :param error: usually use for worker if handling msg failed
        :param on_delivery: callback after producing
        """
        value = _encode_msg(value)
        self._producer.produce(topic, value, on_delivery=on_delivery, headers=dict(error=error))
