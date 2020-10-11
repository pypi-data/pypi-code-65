import datetime
import logging
import json
import sys

from .defaults import *
from . import load_config
from .session import Session, RequestError

class UrlCategories(object):
    def __init__(self, session):
        self.session = session
    def list(self, custom_only=False):
        # [{id, urls[]}]
        path = 'urlCategories'
        if custom_only:
            path += '?customOnly=true'
        return self.session.get(path)
    def create(self, category):
        path = 'urlCategories'
        body = category
        return self.session.post(path, body)
    def list_lite(self):
        pass
    def get_quota(self):
        pass
    def update(self):
        pass
    def delete(self):
        pass
    def lookup(self):
        pass

LOGGER = logging.getLogger(__name__)
if __name__ == '__main__':
    load_config()
    LOGGER.setLevel(logging.DEBUG)
    session = Session()
    categories = UrlCategories(session)
    session.authenticate()
    l = categories.list()
    LOGGER.info(len(l))
    l = categories.list(True)
    LOGGER.info(len(l))
    category = {
        "configuredName": "online blogs test",
        "customCategory": "true",
        "superCategory": "NEWS_AND_MEDIA",
        "type": "URL_CATEGORY",
        "description": "Description",
        "editable": "false",
        "keywords": ["test"],
        "urls": [
            "livejournal.com"
        ]
    }
    try:
        LOGGER.info(categories.create(category))
    except RequestError as exc:
        fmt = 'method {} path {} code {} message {} body {}'
        LOGGER.error(fmt.format(exc.method, exc.path, exc.code, exc.message, exc.body))
