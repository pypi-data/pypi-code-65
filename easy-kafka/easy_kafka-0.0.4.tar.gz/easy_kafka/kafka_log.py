import logging
import threading


class EasyKafkaLog:
    """
    logging, Singleton
    """
    __logger = None
    __instance_lock = threading.Lock()

    @staticmethod
    def logger():
        if EasyKafkaLog.__logger is None:
            with EasyKafkaLog.__instance_lock:
                if EasyKafkaLog.__logger is None:
                    logger = logging.getLogger('easy_kafka_log')
                    logger.setLevel(logging.INFO)
                    # handler, stdout
                    ch = logging.StreamHandler()
                    ch.setLevel(logging.INFO)
                    formatter = logging.Formatter(
                        '[%(asctime)-15s] [%(levelname)s]\t[%(name)s:%(filename)s/%(funcName)s:%(lineno)d]:\t%(message)s')
                    ch.setFormatter(formatter)
                    logger.addHandler(ch)
                    EasyKafkaLog.__logger = logger
        return EasyKafkaLog.__logger

    @staticmethod
    def info(msg):
        EasyKafkaLog.logger().info(msg)
