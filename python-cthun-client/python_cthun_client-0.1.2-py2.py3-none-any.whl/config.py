# -*- coding: utf-8 -*-
__author__ = 'jasonxu'


class Config:
    def __init__(self, api_url=None, access_token=None):
        self._api_url = api_url
        self._access_token = access_token

    @property
    def api_url(self):
        return self._api_url

    @api_url.setter
    def api_url(self, value):
        self._api_url = value

    @property
    def access_token(self):
        if not self._access_token:
            pass
            # raise AuthErrorException("auth error")
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value
