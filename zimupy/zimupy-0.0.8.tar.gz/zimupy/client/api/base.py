# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class BaseZiMuZuAPI(object):
    """ ZiMuZu API base class """
    def __init__(self, client=None):
        self._client = client

    def _get(self, url, **kwargs):
        return self._client.get(url, **kwargs)

    def _post(self, url, **kwargs):
        return self._client.post(url, **kwargs)
