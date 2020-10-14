# -*- coding: utf-8 -*-
__author__ = 'jasonxu'

import requests
from exception import HttpErrorException
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class Connection:
    def __init__(self, config):
        self.config = config

    def _requests_session(self):
        session = requests.Session()
        retry = Retry(
            total=2,
            method_whitelist=['HEAD', 'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            backoff_factor=0.3,
            status_forcelist=(400, 500, 502, 503, 504),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def get(self, url):
        headers = {
            'Authorization': self.config.access_token
        }
        response = self._requests_session().get(url, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise HttpErrorException(e)
        return response.json()

    def post(self, url, data):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.config.access_token,
        }
        response = self._requests_session().post(url, json=data, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise HttpErrorException(e)
        return response.json()

