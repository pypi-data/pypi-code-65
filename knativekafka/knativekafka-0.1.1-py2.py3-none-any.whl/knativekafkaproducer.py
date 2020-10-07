import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
import threading
import logging
import os

class KNativeKafkaProducer(threading.Thread):
    daemon = True
    def __init__(self,topic:str):
        """Initialize using the params
           :param self: KNativeKafkaProducer object           
           :param topic: Kafka topic name 
           Check whether the topic is passed as parameter, if not, get from the os.environ.
           If not avaiable in os.environ, set a default value.
        """
        
        self.logger = logging.getLogger()
        self.logger.info("Initializing Kafka Producer")
        if topic:
            self.topic=topic
        elif 'KAFKA_TOPIC' in os.environ:
            self.topic=os.environ['KAFKA_TOPIC']
        else:
            self.topic="python-topic"
        if 'KAFKA_BOOTSTRAP_SERVERS' in os.environ:
            bootstrap_server=os.environ['KAFKA_BOOTSTRAP_SERVERS']
        else:
           bootstrap_server='localhost:9092'

        self.logger.info(bootstrap_server)
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_server)


    def send_binary_data(self, data:str):
        """Sends the binary data to Kafka topic using the send()
            :param self: KNativeKafkaProducer object
            :param data: A string representing of binary message          
            :return: Message value gets returned
            
        """
        try:
            self.logger.info('Sending the data {} to topic {}'.format(data, self.topic))
            self.producer.send(self.topic, data)
            self.producer.flush(30)
        except KafkaError as e:
            self.logger.error(f'Kafka Error {e}')
            raise Exception(f'Kafka Error {e}')
    
  



