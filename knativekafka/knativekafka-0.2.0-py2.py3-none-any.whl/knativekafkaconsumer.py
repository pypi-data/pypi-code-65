# Serialize json messages
import json
import logging
import base64
import os
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import threading
import time

class KNativeKafkaConsumer(threading.Thread):
    daemon = True    

    def __init__(self,topics:str):

        """
        Initialize a KNativeKafkaConsumer class based on the input params and the environment variables.
        Parameters
        ----------
           :param self: KNativeKafkaConsumer object                 
           :param topics: Kafka topic name
           Check whether the topic is passed as parameter, if not, get from the os.environ.

        """
        self.logger = logging.getLogger()
        self.logger.info("Initializing Kafka Consumer")
        if topics:
            self.topics=topics
        elif 'KAFKA_TOPIC' in os.environ:
            self.topics=os.environ['KAFKA_TOPIC']
        else:
            raise ValueError('Topic is required!')
                    
 
        bootstrap_server=os.getenv('KAFKA_BOOTSTRAP_SERVERS',default='localhost:9092')
        is_tls_enable=os.getenv('KAFKA_NET_TLS_ENABLE',default='False')
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
        self.consumer=KafkaConsumer(
                      bootstrap_servers=bootstrap_server,                                                                                                                                                                                                                                                                                                                            
                      auto_offset_reset='earliest',
                      value_deserializer=bytes.decode,
                      security_protocol=self.security_protocol,
                      ssl_cafile=self.ssl_cafile,
                      ssl_certfile=self.ssl_certfile,
                      ssl_keyfile=self.ssl_keyfile)
        
    def getMessage(self) -> str:
        """
        Get the message
        Parameters
        ----------
            :param self: KNativeKafkaConsumer object               
        Returns
        -------                    
            :return: message value
        """
        print("**** Print the Messages ****")
        self.consumer.subscribe([self.topics])
        for message in self.consumer:
            print("topic={} partition={} offset={} key={} value={}".format(message.topic,
                                                                        message.partition,
                                                                        message.offset,
                                                                        message.key,
                                                                        message.value))
        return message.value