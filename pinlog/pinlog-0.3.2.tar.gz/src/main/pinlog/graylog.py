import logging
import graypy

class Graylog(Log):
    def __init__(self, config):
        self._config = config
        self.logger = logging.getLogger('test_logger')
        self.logger.setLevel(logging.DEBUG)

        handler = graypy.GELFUDPHandler('localhost', 12201)
        self.logger.addHandler(handler)

        self.logger.addFilter(self.UsernameFilter())

    class UsernameFilter(logging.Filter):
        def __init__(self):
            self.username = 'TEST'

        def filter(self, record):
            record.username = self.username
            return True

    def send_log(data):
        self.logger.debug('Send to Graylog:', data)