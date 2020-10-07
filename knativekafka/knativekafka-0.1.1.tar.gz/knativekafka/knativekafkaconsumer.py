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

    def __init__(self,topic:str):
        """Initialize using the params
           :param self: KNativeKafkaConsumer object                 
           :param topic: Kafka topic name
           Check whether the topic is passed as parameter, if not, get from the os.environ.
           If not avaiable in os.environ, set a default value.
        """
        self.logger = logging.getLogger()
        self.logger.info("Initializing Kafka Consumer")
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
        self.consumer = KafkaConsumer(bootstrap_servers=bootstrap_server,
                            auto_offset_reset='earliest',
                            value_deserializer=bytes.decode)
        
    def getMessage(self) -> str:
        """Get the message
            :param self: KNativeKafkaConsumer object           
            :param server: Kafka bootstrap server      
            :param topic: Kafka topic name                   
            :return: none
        """
        print("**** Print the Messages ****")
        self.consumer.subscribe([self.topic])
        for message in self.consumer:
            print("topic={} partition={} offset={} key={} value={}".format(message.topic,
                                                                        message.partition,
                                                                        message.offset,
                                                                        message.key,
                                                                        message.value))
        return message.value
                


        
