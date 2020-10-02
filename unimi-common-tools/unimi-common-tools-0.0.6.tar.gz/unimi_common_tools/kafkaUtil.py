import os
import logging
from confluent_kafka import Producer, Consumer


logger = logging.getLogger(__name__)
CONFIG = {'bootstrap.servers': os.getenv('KAFKA_TOPIC_SERVER')}


class KafkaUtil:
    def __init__(self, conf=None):
        self.conf = conf or CONFIG
        self.producer = Producer(self.conf)

    def new_consumer(self):
        conf = {
            'group.id': 'mygroup',
            'auto.offset.reset': 'earliest',
            'auto.commit.interval.ms': 1000
        }
        conf.update(**self.conf)
        logger.info('Creating New Consumer')
        return Consumer(conf)

    def publish(self, topic_name, key, value):
        # Asynchronously produce a message, the delivery report callback
        # will be triggered from poll() above, or flush() below, when the message has
        # been successfully delivered or failed permanently.
        logger.info('Pulishing msg on topic {0} for {1}: {2}'.format(topic_name, key, value))
        self.producer.produce(topic_name, value.encode('utf-8'), key, callback=delivery_report)

        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
        self.producer.flush()

    def consume(self, consumer, topic, redirect, publish_to=None, publish_topic=None):
        consumer.subscribe([topic])
        logger.info('Consuming messages for :{}'.format(topic))

        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                logger.info("Consumer error: {}".format(msg.error()))
                continue

            logger.info('Received message: {} for {}'.format(msg.value().decode('utf-8'), topic))
            msg = msg.value().decode('utf-8')
            logger.info("Extracted msg is: {}".format(str(msg)))
            logger.info("Calling {}".format(str(redirect.__name__)))
            try:
                op = redirect(msg)
            except Exception as e:
                logger.error(e)

            logger.info('post operation {}'.format(str(redirect.__name__)))
        
            if publish_to:
                self.publish(publish_to, publish_topic, op)
            
        consumer.close()


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        logger.info('Message delivery failed: {}'.format(err))
    else:
        logger.info('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))



