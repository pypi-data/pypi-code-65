import asyncio
import json
import math
from collections.abc import Callable
from functools import partial
from inspect import iscoroutinefunction, ismethod, isfunction, isbuiltin, isclass
from json import JSONDecodeError
from typing import Union

from confluent_kafka.cimpl import Consumer, Message

from plain_kafka.logger import LOGGER
from plain_kafka.producer import AsyncProducer


def _decode_msg_value(msg: Union[str, bytes]):
    if isinstance(msg, bytes):
        msg = msg.decode('utf-8')
    try:
        msg = json.loads(msg)
    except JSONDecodeError:
        LOGGER.warning('Message {} is not dict.'.format(msg))
    return msg


def get_call_repr(func: Callable, *args, **kwargs) -> str:
    """Return the string representation of the function call.
    :param func: A callable (e.g. function, method).
    :type func: callable
    :param args: Positional arguments for the callable.
    :param kwargs: Keyword arguments for the callable.
    :return: String representation of the function call.
    :rtype: str
    """
    # Functions, builtins and methods
    if ismethod(func) or isfunction(func) or isbuiltin(func):
        func_repr = '{}.{}'.format(func.__module__, func.__qualname__)
    # A callable class instance
    elif not isclass(func) and hasattr(func, '__call__'):
        func_repr = '{}.{}'.format(func.__module__, func.__class__.__name__)
    else:
        func_repr = repr(func)

    args_reprs = [repr(arg) for arg in args]
    kwargs_reprs = [k + '=' + repr(v) for k, v in sorted(kwargs.items())]
    return '{}({})'.format(func_repr, ', '.join(args_reprs + kwargs_reprs))


# TODO write sync worker too.
class AsyncWorker(object):
    """
    Fetches from Kafka topics and processes them.

    :param consumer_topic: Name of the Kafka topic for consume.
    :type consumer_topic: str
    :param service: Service function which is executed every time when job is processed.
    Service must get as argument str or dict type object.
    :type service: callable
    :param consumer_conf: config for Kafka consumer.
    :type consumer_conf: dict
    :param failed_topic: Kafka topic for produce unprocessed messages from consumer_topic.
    :type failed_topic: str
    :param producer_conf: config for Kafka producer for producing unprocessed messages.
    :type producer_conf: dict
    """

    def __init__(self, consumer_topic: str, service: Callable,
                 consumer_conf: dict, failed_topic: str, producer_conf: dict):

        self._consumer_topic = consumer_topic
        self._consumer = Consumer(consumer_conf)
        self._service = service
        self._failed_topic = failed_topic  # use naming like <project name>_<version>_<consumer_topic><retry/failed>
        self._producer = AsyncProducer(producer_conf)

    def __repr__(self):
        """Return the string representation of the worker.
        :return: String representation of the worker.
        :rtype: str
        """

        return 'Worker(Consumer={}, consume_topic={})'.format(self._consumer, self._consumer_topic)

    def __del__(self):  # pragma: no cover
        # noinspection PyBroadException
        try:
            self._consumer.close()
        except Exception:
            pass

    async def _exec_service(self, message_value):
        if iscoroutinefunction(self._service):
            res = await self._service(message_value)
        else:
            res = self._service(message_value)
        return res

    async def _process_message(self, msg: Message):
        """
        De-serialize message and execute service.
        :param msg: Kafka message.
        :type msg: confluent_kafka.Message`
        """
        LOGGER.info('Processing Message(topic={}, partition={}, offset={}) ...'.format(msg.topic, msg.partition,
                                                                                       msg.offset))
        service_repr = get_call_repr(self._service)
        LOGGER.info('Executing job {}'.format(service_repr))
        try:
            message_value = _decode_msg_value(msg.value())
            res = await self._exec_service(message_value)

        except KeyboardInterrupt:
            LOGGER.error('Job was interrupted: {}'.format(msg.offset()))

        except Exception as err:
            LOGGER.exception('Job {} raised an exception: {}'.format(msg.offset(), err))

            await self._producer.produce(topic=self._failed_topic, value=msg.value(), error=str(err))
        else:
            LOGGER.info('Job {} returned: {}'.format(msg.offset(), res))

    @property
    def consumer_topic(self):
        """Return the name of the Kafka topic.
        :return: Name of the Kafka topic.
        :rtype: str
        """
        return self._consumer_topic

    @property
    def consumer(self):
        """Return the Kafka consumer instance.
        :return: Kafka consumer instance.
        :rtype: kafka.KafkaConsumer
        """
        return self._consumer

    @property
    def service(self):
        """Return the service function.
        :return: Callback function, or None if not set.
        :rtype: callable | None
        """
        return self._service

    async def start(self, max_messages: int = math.inf, commit_offsets: bool = True) -> int:
        """Start processing Kafka messages and executing jobs.
        :param max_messages: Maximum number of Kafka messages to process before stopping. If not set, worker runs until
        interrupted.

        :type max_messages: int
        :param commit_offsets: If set to True, consumer offsets are committed every time a message is processed
        (default: True).
        :type commit_offsets: bool
        :return: Total number of messages processed.
        :rtype: int
        """
        LOGGER.info('Starting {} ...'.format(self))

        self._consumer.unsubscribe()
        self._consumer.subscribe([self.consumer_topic])
        LOGGER.info(" Try get messages from position: {}".format(self._consumer.position(self._consumer.assignment())))
        messages_processed = 0
        while messages_processed < max_messages:
            loop = asyncio.get_event_loop()
            # awaiting place for processing messages in other coroutines
            messages = await loop.run_in_executor(None, partial(self._consumer.consume, 10, 2.0))
            LOGGER.debug(" Try get messages from position: {}".format(
                self._consumer.position(self._consumer.assignment())))
            if not messages:
                LOGGER.debug("Messages not found")
                continue
            for msg in messages:
                if msg.error():
                    LOGGER.error("Consumer error: {}".format(msg.error()))
                LOGGER.info("Get message with offset {}".format(msg.offset()))
                asyncio.create_task(self._process_message(msg))
            if commit_offsets:
                self._consumer.commit()

            messages_processed += 1
        self._consumer.close()
        return messages_processed


class AsyncRetryWorker(AsyncWorker):
    """
    If service in base Worker failed, RetryWorker fetch to Kafka "..._retry" topic and execute service again.
    If service in RetryWorker will failed again, produce msg to "failed" Kafka topic.
    """
    async def _retry_exec(self, count, timeout, msg):
        """
        Executing service by scheduling. Scheduling realised on asynchronous features in one thread.
        :param count: how much times service should be restarted
        :param timeout: timeout between restarting in seconds
        :param msg: kafka msg value
        :return:
        True: if service finishing with success
        (False, errors): if service failed again and list service errors
        """
        errors = []
        for _ in range(count):
            try:
                await asyncio.sleep(timeout)
                await self._exec_service(msg)
            except Exception as err:
                errors.append(err)
                LOGGER.error('Retry-worker executing failed with err: {}'.format(err))
                continue
            return True, None  # success
        return False, errors  # failed

    async def _process_message(self, msg: Message):
        """
        De-serialize message and execute service.
        :param msg: Kafka message.
        :type msg: confluent_kafka.Message`
        """
        LOGGER.info('Processing Message(topic={}, partition={}, offset={}) ...'.format(msg.topic, msg.partition,
                                                                                       msg.offset))
        errors = []
        service_repr = get_call_repr(self._service)
        # TODO get schedule from args
        # First element in tuple is count, the second is timeout in sec.
        schedule = [(3, 5), (2, 60), (2, 60*5), (1, 60*60), (3, 60*60*3)]
        LOGGER.info('Executing job {}'.format(service_repr))
        try:
            message_value = _decode_msg_value(msg.value())
            for count, timeout in schedule:
                res, exec_error = await self._retry_exec(count, timeout, message_value)
                if res:
                    LOGGER.info('Successful re-processing of the message {} by the service {}'.format(message_value,
                                                                                                      self.service))
                    break
                else:
                    errors.extend(exec_error)
            if len(errors) > 0:
                await self._producer.produce(topic=self._failed_topic, value=msg.value(), error=str(errors))

        except KeyboardInterrupt:
            LOGGER.error('Job was interrupted: {}'.format(msg.offset()))

        except Exception as err:
            LOGGER.exception('Job {} raised an exception: {}'.format(msg.offset(), err))
            errors.append(err)

            # For handle analyse and process message
            await self._producer.produce(topic=self._failed_topic, value=msg.value(), error=str(errors))
        else:
            LOGGER.info('Job {} finished'.format(msg.offset()))
