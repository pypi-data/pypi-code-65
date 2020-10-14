import os
import requests
import logging
from urllib.parse import urlencode, quote
from requests.exceptions import HTTPError

from pyrasgo.logger import HeapLogger, LocalLogger, DOMAINS, LOCAL, PRODUCTION


class InvalidApiKeyException(Exception):
    pass


class Connection(object):
    """
    Base class for all Rasgo objects to facilitate API calls.
    """

    def __init__(self, api_key=None):
        self._api_key = api_key
        if self.__class__.__name__ == 'Connection':
            if self.verify_credentials():
                raise InvalidApiKeyException(f"The API key provided ({api_key[:5]}...{api_key[-5:]}) is not valid.")
        else:
            if not api_key:
                raise ValueError("The API key must be provided to the constructor if not built by Connection.")

        self._hostname = os.environ.get("RASGO_DOMAIN", DOMAINS[PRODUCTION])
        user_profile = self._get_profile()
        self._user_id = user_profile.get('id')
        self._event_logger = self._set_up_logging(user_profile)
        logging.info(f"Setup logger: {self._event_logger.__class__}")

    def _set_up_logging(self, user_profile):
        if self._hostname == DOMAINS[LOCAL]:
            return LocalLogger(user_profile)
        return HeapLogger(user_profile, hostname=self._hostname)

    def verify_credentials(self) -> bool:
        """
        Verify the API key provide is valid and can connect to Rasgo.
        """
        try:
            self._get('/users/me', api_version=1)
        except HTTPError as e:
            if e.response.status_code == '401':
                return False
            else:
                raise e
        return True

    def _get_profile(self):
        return self._get('/users/me', api_version=1).json()

    def _url(self, resource, api_version=None):
        if '/' == resource[0]:
            resource = resource[1:]
        return f"https://{self._hostname}/{'' if api_version is None else f'v{api_version}/' }{resource}"

    def find(self, resource, equality_filters):
        search_strings = []
        for k, v in equality_filters.items():
            filterstr = k + "||$eq||" + v
            search_strings.append(filterstr)
        params = {
            "filter": search_strings
        }
        params = urlencode(params, quote_via=quote, doseq=True)
        response = self._get(resource, params)
        if response.status_code == 404:
            return None
        else:
            response.raise_for_status()
            return response.json()

    def _get(self, resource, params=None, api_version=None) -> requests.Response:
        """
        Performs GET request to Rasgo API as defined within the class instance.

        :param endpoint: Target resource to GET from API.
        :param params: Additional parameters to specify for GET request.
        :return: Response object containing content returned.
        """
        response = requests.get(self._url(resource, api_version),
                                headers=self._headers(self._api_key),
                                params=params or {})
        response.raise_for_status()
        return response

    def _patch(self, resource, _json=None, params=None, api_version=None) -> requests.Response:
        """
        Performs PATCH request to Rasgo API as defined within the class instance.

        :param resource: Target resource to POST from API.
        :param _json: JSON object to send in POST request
        :param params: Additional parameters to specify for POST request.
        :return: Response object containing content returned.
        """
        response = requests.patch(self._url(resource, api_version),
                                  json=_json,
                                  headers=self._headers(self._api_key),
                                  params=params or {})
        response.raise_for_status()
        return response

    def _post(self, resource, _json=None, params=None, api_version=None) -> requests.Response:
        """
        Performs POST request to Rasgo API as defined within the class instance.

        :param resource: Target resource to POST from API.
        :param _json: JSON object to send in POST request
        :param params: Additional parameters to specify for POST request.
        :return: Response object containing content returned.
        """
        response = requests.post(self._url(resource, api_version),
                                 json=_json,
                                 headers=self._headers(self._api_key),
                                 params=params or {})
        response.raise_for_status()
        return response

    def _get_items(self, resource, equality_filters):
        search_strings = []
        for k, v in equality_filters.items():
            filterstr = k + "||$eq||" + v
            search_strings.append(filterstr)
        params = {
            "filter": search_strings
        }
        params = urlencode(params, quote_via=quote, doseq=True)
        try:
            response = self._get(resource, params)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e
        if response.status_code == 404:
            return None
        else:
            response.raise_for_status()
            return response.json()

    def _get_item(self, resource, equality_filters, allow_multiple=False):
        results = self._get_items(resource, equality_filters)
        if results is None:
            return None
        elif 1 < len(results):
            if allow_multiple:
                return results[-1]
            else:
                raise ValueError("Multiple returned for {}, check your filters".format(resource))
        elif 0 == len(results):
            return None
        else:
            return results[0]

    @staticmethod
    def _headers(api_key) -> dict:
        if not api_key:
            raise ValueError("Must provide an API key to access the endpoint")
        return {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
