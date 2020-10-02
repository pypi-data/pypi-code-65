
import requests
import logging

"""
rabona-python is a simple wrapper around Rabona (rabona.io) API. It wraps
the generic request-building into simple Python methods over the RabonaClient
instance so that applications can interact with the Rabona. 

Currently only one-way is supported - so you can only fetch data, but in the 
future it's also planned to create corresponding Hive Blockchain CustomJson
objects to interact with the game.
"""

RABONA_API_BASE_URL = 'https://api.rabona.io/'


class RabonaClient:
    """A simple Rabona client wrapper over the requests library."""

    def __init__(self, base_url=None, loglevel=logging.ERROR):
        self.base_url = base_url or RABONA_API_BASE_URL
        self.logger = None
        self.set_logger(loglevel)

    def __getattr__(self, attr):
        """Map function name to path, arguments into
        query string, dynamically."""
        def callable(*args, **kwargs):
            return self._request(attr, *args, **kwargs)

        return callable

    def set_logger(self, loglevel):
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(loglevel)

    def _request(self, path, **query_string):
        self.logger.info("Sending request to: %s with args: %s",
                         self.base_url + path, query_string)
        response = requests.get(self.base_url + path, params=query_string)
        response.raise_for_status()
        self.logger.debug("Response: %s", response.text)
        return response.json()
