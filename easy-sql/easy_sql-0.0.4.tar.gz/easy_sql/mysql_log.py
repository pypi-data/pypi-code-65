import logging
import threading


class EasyMySQLLog:
    """
    logging, Singleton
    """
    __logger = None
    __instance_lock = threading.Lock()

    @staticmethod
    def logger():
        if EasyMySQLLog.__logger is None:
            with EasyMySQLLog.__instance_lock:
                if EasyMySQLLog.__logger is None:
                    logger = logging.getLogger('easy_sql_log')
                    logger.setLevel(logging.INFO)
                    # handler, stdout
                    ch = logging.StreamHandler()
                    ch.setLevel(logging.INFO)
                    formatter = logging.Formatter(
                        '[%(asctime)-15s] [%(levelname)s]\t[%(name)s:%(filename)s/%(funcName)s:%(lineno)d]:\t%(message)s')
                    ch.setFormatter(formatter)
                    logger.addHandler(ch)
                    EasyMySQLLog.__logger = logger
        return EasyMySQLLog.__logger

    @staticmethod
    def info(msg):
        EasyMySQLLog.logger().info(msg)
