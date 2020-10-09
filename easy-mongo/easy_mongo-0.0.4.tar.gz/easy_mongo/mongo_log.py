import logging
import threading


class EasyMongoLog:
    """
    logging, Singleton
    """
    __logger = None
    __instance_lock = threading.Lock()

    @staticmethod
    def logger():
        if EasyMongoLog.__logger is None:
            with EasyMongoLog.__instance_lock:
                if EasyMongoLog.__logger is None:
                    logger = logging.getLogger('easy_mongo_log')
                    logger.setLevel(logging.INFO)
                    # handler, stdout
                    ch = logging.StreamHandler()
                    ch.setLevel(logging.INFO)
                    formatter = logging.Formatter(
                        '[%(asctime)-15s] [%(levelname)s]\t[%(name)s:%(filename)s/%(funcName)s:%(lineno)d]:\t%(message)s')
                    ch.setFormatter(formatter)
                    logger.addHandler(ch)
                    EasyMongoLog.__logger = logger
        return EasyMongoLog.__logger

    @staticmethod
    def info(msg):
        EasyMongoLog.logger().info(msg)
