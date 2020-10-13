import requests

import datetime
import hashlib
import json
import logging
import inspect


class TimeTapAuthentication(requests.auth.AuthBase):

    logging.basicConfig(filename='auth.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

    def __init__(self, APIKey: str, PrivateKey: str):
        self.APIKey = APIKey
        self.PrivateKey = PrivateKey
        self.timestamp = datetime.datetime.now().timestamp()

    def get_authorization_header(self):
        signature = hashlib.md5((self.APIKey + self.PrivateKey).encode('utf-8')).hexdigest()
        token = requests.get(url=f'https://api.timetap.com/live/sessionToken?apiKey={self.APIKey}&timestamp={self.timestamp}&signature={signature}')
        token = json.loads(token.text)
        return 'Bearer ' + token['sessionToken']

    def __call__(self, request):
        logging.info(f'Starting {inspect.currentframe().f_code.co_name}')
        request.headers['Authorization'] = self.get_authorization_header()
        logging.info(f'Request Authorization Header: {request.headers["Authorization"]}')
        logging.debug(f'URL: {request.url}')
        logging.debug(f'Request Headers: {request.headers.items()}')
        logging.info(f'Finishing {inspect.currentframe().f_code.co_name}')
        return request
