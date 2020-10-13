import os
from heapapi import HeapAPIClient 
import requests
from urllib.parse import urlencode, quote
from requests.exceptions import HTTPError
from pyrasgo.version import __version__

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
        
        self._set_up_logging()
        self._event_logger.track(
            identity=self._user_id,
            event="pyrasgo: connection",
            properties=self._event_properties
        )

    def _set_up_logging(self):
        #set session vars
        _prod_domain = 'api.rasgoml.com'
        self._hostname = os.environ.get("RASGO_DOMAIN", _prod_domain)
        self._version = __version__
        #set user vars
        _user_profile = self._get_profile()
        self._user_id = _user_profile['userId']
        self._username = _user_profile['username']
        self._org_id = _user_profile['orgId']
        #set up Heap
        if self._hostname == _prod_domain:
            self._heap_key = '540300130' #prod acct
        else:
            self._heap_key = '3353132567' #dev acct
        self._event_logger = HeapAPIClient(self._heap_key)
        self._event_properties = {"host":self._hostname,
                                "version":self._version,
                                "username":self._username,
                                "orgId":self._org_id
        }

    def verify_credentials(self) -> bool:
        """
        Verify the API key provide is valid and can connect to Rasgo.
        """
        try:
            self._get('/profile')
        except HTTPError as e:
            if e.response.status_code == '401':
                return False
            else:
                raise e
        return True

    def _get_profile(self):
        response = self._get('/profile')
        return response.json()

    def _url(self, resource):
        if '/' == resource[0]:
            resource = resource[1:]
        return f'https://{self._hostname}/{resource}'

    def find(self, resource, equality_filters):
        search_strings = []
        for k,v  in equality_filters.items():
            filterstr = k + "||$eq||" + v
            search_strings.append(filterstr)
        params = {
            "filter": search_strings
            }
        params = urlencode(params, quote_via=quote, doseq = True)
        response = self._get(resource, params)
        if response.status_code == 404:
            return None
        else:
            response.raise_for_status()
            return response.json()

    def _get(self, endpoint, params=None) -> requests.Response:
        """
        Performs GET request to Rasgo API as defined within the class instance.

        :param endpoint: Target resource to GET from API.
        :param params: Additional parameters to specify for GET request.
        :return: Response object containing content returned.
        """
        url = self._url(endpoint)
        response = requests.get(url,
                                headers=self._headers(self._api_key),
                                params=params or {})
        response.raise_for_status()
        return response

    def _patch(self, resource, _json=None, params=None) -> requests.Response:
        """
        Performs PATCH request to Rasgo API as defined within the class instance.

        :param resource: Target resource to POST from API.
        :param _json: JSON object to send in POST request
        :param params: Additional parameters to specify for POST request.
        :return: Response object containing content returned.
        """
        response = requests.patch(self._url(resource),
                                  json=_json,
                                  headers=self._headers(self._api_key),
                                  params=params or {})
        response.raise_for_status()
        return response

    def _post(self, resource, _json=None, params=None) -> requests.Response:
        """
        Performs POST request to Rasgo API as defined within the class instance.

        :param resource: Target resource to POST from API.
        :param _json: JSON object to send in POST request
        :param params: Additional parameters to specify for POST request.
        :return: Response object containing content returned.
        """
        response = requests.post(self._url(resource),
                                 json=_json,
                                 headers=self._headers(self._api_key),
                                 params=params or {})
        response.raise_for_status()
        return response

    def _get_items(self, resource, equality_filters):
        search_strings = []
        for k,v  in equality_filters.items():
            filterstr = k + "||$eq||" + v
            search_strings.append(filterstr)
        params = {
            "filter": search_strings
            }
        params = urlencode(params, quote_via=quote, doseq = True)
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

    def _get_item(self, resource, equality_filters, allow_multiple = False):
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


