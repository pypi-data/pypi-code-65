import logging
import threading


class EasyRedisLog:
    """
    logging, Singleton
    """
    __logger = None
    __instance_lock = threading.Lock()

    @staticmethod
    def logger():
        if EasyRedisLog.__logger is None:
            with EasyRedisLog.__instance_lock:
                if EasyRedisLog.__logger is None:
                    logger = logging.getLogger('easy_redis_log')
                    logger.setLevel(logging.INFO)
                    # handler, stdout
                    ch = logging.StreamHandler()
                    ch.setLevel(logging.INFO)
                    formatter = logging.Formatter(
                        '[%(asctime)-15s] [%(levelname)s]\t[%(name)s:%(filename)s/%(funcName)s:%(lineno)d]:\t%(message)s')
                    ch.setFormatter(formatter)
                    logger.addHandler(ch)
                    EasyRedisLog.__logger = logger
        return EasyRedisLog.__logger

    @staticmethod
    def info(msg):
        EasyRedisLog.logger().info(msg)
