import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
import threading
import logging
import os

class KNativeKafkaProducer(threading.Thread):
    daemon = True
    def __init__(self,topic:str):

        """
        Initialize a KNativeKafkaProducer class based on the input params and the environment variables.
        Parameters
        ----------
           :param self: KNativeKafkaProducer object           
           :param topic: Kafka topic name 
           Check whether the topic is passed as parameter, if not, get from the os.environ.
           Get the other parameters from the environment variable(s).
        """
        
        self.logger = logging.getLogger()
        self.logger.info("Initializing Kafka Producer")
        if topic:
            self.topic=topic
        elif 'KAFKA_TOPIC' in os.environ:
            self.topic=os.environ['KAFKA_TOPIC']
        else:
            raise ValueError( 'Topic is required!')
                   
        self.logger.info("Topic")
        self.logger.info(topic)

        self.bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS',default='localhost:9092')
        
        self.logger.info(self.bootstrap_servers)
        
        is_tls_enable=os.getenv('KAFKA_NET_TLS_ENABLE',default='False')
        self.logger.info(is_tls_enable)
        if is_tls_enable == 'True':
            self.security_protocol="SSL"
            if 'KAFKA_NET_TLS_CA_CERT' not in os.environ:
                raise ValueError( 'TLS CA Certificate is required!')
            if 'KAFKA_NET_TLS_CERT' not in os.environ:
                raise ValueError( 'TLS Certificate is required!')
            if 'KAFKA_NET_TLS_KEY' not in os.environ:
                raise ValueError( 'TLS Key is required!')
            self.ssl_cafile=os.environ['KAFKA_NET_TLS_CA_CERT']
            self.ssl_certfile=os.environ['KAFKA_NET_TLS_CERT']
            self.ssl_keyfile=os.environ['KAFKA_NET_TLS_KEY']
        else:
            self.security_protocol="PLAINTEXT"
            self.ssl_cafile=None
            self.ssl_certfile=None
            self.ssl_keyfile=None
       
        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                        security_protocol=self.security_protocol,
                        ssl_cafile=self.ssl_cafile,
                        ssl_certfile=self.ssl_certfile,
                        ssl_keyfile=self.ssl_keyfile
                        )

    def send_binary_data(self, data:str):
        """
        Sends the binary data to Kafka topic using the send()
        Parameters
        ----------
            :param self: KNativeKafkaProducer object
            :param data: A string representing a binary message 

        """
        try:
            self.logger.info('Sending the data {} to topic {}'.format(data, self.topic))
            self.producer.send(self.topic, data)
            self.producer.flush(30)
        except KafkaError as e:
            self.logger.error(f'Kafka Error {e}')
            raise Exception(f'Kafka Error {e}')