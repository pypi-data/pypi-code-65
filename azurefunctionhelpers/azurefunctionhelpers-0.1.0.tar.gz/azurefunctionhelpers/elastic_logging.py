import functools
import logging
from elasticapm import Client, instrument
from elasticapm.handlers.logging import LoggingHandler


def log(tran_category: str, tran_name: str, ok_status: str = 'ok', error_status: str = 'error') -> callable:
    """
    Intercepts function call for logging to Elastic APM
    :param str tran_category: Category to log the transaction as
    :param str tran_name: Name for the transaction
    :param str ok_status: Status to log OK as
    :param str error_status: Status to log error as
    :return: Function wrapper
    :rtype: Function
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(req):
            try:
                instrument()
                client = Client()
                handler = LoggingHandler()
                logger = logging.getLogger()
                logger.addHandler(handler)
                client.begin_transaction(tran_category)

                result = func(req)

                client.end_transaction(tran_name, ok_status)

                return result

            except Exception as e:
                logging.error(e, exc_info=True)
                client.end_transaction(tran_name, error_status)
                raise

        return wrapper
    return decorator
