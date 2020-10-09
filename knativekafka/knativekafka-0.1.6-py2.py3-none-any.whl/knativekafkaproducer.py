import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
import threading
import logging
import os

class KNativeKafkaProducer(threading.Thread):
    daemon = True
  
                          
   

    def __init__(self,topic:str,security_protocol='PLAINTEXT',
                          ssl_cafile=None,
                          ssl_certfile=None,
                          ssl_keyfile=None
                          ):
   
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
         #'KAFKA_BOOTSTRAP_SERVERS' in os.environ:
        bootstrap_server=os.getenv('KAFKA_BOOTSTRAP_SERVERS',default='localhost:9092')
        print("kafka server")
        print(bootstrap_server)
        print(os.getenv('KAFKA_NET_TLS_ENABLE'))
        value=os.getenv('KAFKA_NET_TLS_ENABLE',default=False)
        print("kafka tls")
        print(value)
        print("KAFKA_NET_TLS_CERT")
        print(os.environ['KAFKA_NET_TLS_CERT']) # if value in os.environ else False

        value = 'KAFKA_NET_TLS_CERT' in os.environ
        # ssl_check_hostname = os.environ['KAFKA_NET_TLS_ENABLE'] if value in os.environ else False
        # self.ssl_cafile = 

        self.security_protocol=security_protocol
        #self.ssl_check_hostname=ssl_check_hostname
        self.ssl_cafile=ssl_cafile
        self.ssl_certfile=ssl_certfile
        self.ssl_keyfile=ssl_keyfile

        self.logger.info(bootstrap_server)
       
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_server,
                        security_protocol=security_protocol,
                        # ssl_check_hostname=ssl_check_hostname,
                        ssl_cafile=ssl_cafile,
                        ssl_certfile=ssl_certfile,
                        ssl_keyfile=ssl_keyfile
                        )

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
    
  



