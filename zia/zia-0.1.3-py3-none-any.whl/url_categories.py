import datetime
import logging
import json
import sys

import fire

from zia.defaults import *
from zia import load_config, ZiaApiBase
from zia.session import Session, RequestError

class UrlCategories(ZiaApiBase):
    def list(self, custom_only=False):
        path = 'urlCategories'
        if custom_only:
            path += '?customOnly=true'
        return self._output(self._session.get(path))
    def create(self, category):
        path = 'urlCategories'
        return self._output(self._session.post(path, category))
    def list_lite(self):
        path = 'urlCategories/lite'
        return self._output(self._session.get(path))
    def get_quota(self):
        path = 'urlCategories/urlQuota'
        return self._output(self._session.get(path))
    def get(self, category_id):
        path = 'urlCategories/{}'.format(category_id)
        return self._output(self._session.get(path))
    def update(self, category_id, category):
        path = 'urlCategories/{}'.format(category_id)
        return self._output(self._session.put(path, category))
    def delete(self, category_id):
        path = 'urlCategories/{}'.format(category_id)
        return self._output(self._session.delete(path))
    def lookup(self, urls):
        path = 'urlLookup'
        return self._output(self._session.post(path, urls))

LOGGER = logging.getLogger(__name__)
if __name__ == '__main__':
    try:
        load_config()
        LOGGER.setLevel(logging.DEBUG)
        session = Session()
        categories = UrlCategories(session, 'str')
        session.authenticate()
        fire.Fire(categories)
    except RequestError as exc:
        fmt = 'method {} path {} code {} message {} body {}'
        LOGGER.error(fmt.format(exc.method, exc.path, exc.code, exc.message, exc.body))
