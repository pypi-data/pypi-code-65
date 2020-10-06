import logging
import random
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from .exceptions import NoConfigException, ConfigFormatException, FeedNotFoundException

logger = logging.getLogger("signalfeed")


class Signalfeed:
    def __init__(self, config=None):
        self.config = config
        self.endpoint = None
        self.executor = ThreadPoolExecutor(2)

    def setup(self, config, endpoint=None):
        if type(config) is not dict:
            raise ConfigFormatException("Please provide configuration as dictionary object")

        self.config = config

        if endpoint is None:
            endpoint = "https://signalfeed.app/api/v1/signal"

        self.endpoint = endpoint

    def send_signal(self, data):
        success = False
        try:
            r = urllib.request.urlopen(self.endpoint, data)
            success = r.getcode() == 200
        except Exception as e:
            logger.debug("Send signal exception: {}".format(e))

        if success:
            return True

        # sleep some time and send again
        time.sleep(random.randint(1, 5))
        self.executor.submit(self.send_signal, data)

    def signal(self, feed, message):
        if self.config is None:
            raise NoConfigException("Config is not provided")

        token = self.config.get(feed)
        if not token:
            raise FeedNotFoundException("Feed \"{}\" not found in config".format(feed))

        # prepare data
        data = urllib.parse.urlencode({'token': token, 'message': message})
        data = data.encode('ascii')
        # send to thread pool
        self.executor.submit(self.send_signal, data)


signalfeed = Signalfeed()
