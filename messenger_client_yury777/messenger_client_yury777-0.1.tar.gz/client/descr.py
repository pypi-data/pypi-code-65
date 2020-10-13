import logging
import sys

if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


class Port:
    def __set__(self, instance, listen_port):
        if not listen_port in range(1024, 65536):
            logger.critical(
                f'Попытка запуска сервера с указанием неподходящего порта '
                f'{listen_port}. Допустимы адреса с 1024 до 65535.')
            sys.exit(1)
        instance.__dict__[self.name] = listen_port

    def __set_name__(self, owner, name):
        self.name = name
