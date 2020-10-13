
import os
import logging
import functools
from . import elastic_apm

scheme_str = os.environ.get('OBSERVABILITY_SCHEME', '').lower()

scheme_map = {
    'elastic_apm': elastic_apm
}
scheme = scheme_map.get(scheme_str)


if scheme:
    log = scheme.log
    log_async = scheme.log_async
else:
    def log(tran_category: str, tran_name: str = 'None', ok_status: str = 'ok', error_status: str = 'error') -> callable:
        """
        For use as a decorator to wrap Azure function calls.
        :param str tran_category: Category to log the transaction as
        :param str tran_name: Name for the transaction
        :param str ok_status: Status to log OK as
        :param str error_status: Status to log error as
        :return: Function wrapper
        :rtype: Function
        """

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.error(e, exc_info=True)
                    raise

            return wrapper
        return decorator

    def log_async(tran_category: str, tran_name: str = 'None', ok_status: str = 'ok', error_status: str = 'error') -> callable:
        """
        For use as a decorator to wrap async Azure function calls.
        :param str tran_category: Category to log the transaction as
        :param str tran_name: Name for the transaction
        :param str ok_status: Status to log OK as
        :param str error_status: Status to log error as
        :return: Function wrapper
        :rtype: Function
        """

        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logging.error(e, exc_info=True)
                    raise

            return wrapper
        return decorator
