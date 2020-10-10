from typing import Union
import logging
import os

from tokko_locations_client.models import (
    Country,
    State,
    Location
)

from requests.exceptions import (
    HTTPError,
    ConnectionError
)
import requests

from tokko_locations_client.exceptions import (
    APIConnectionError,
    DataNotFoundError,
)


__all__ = [
    "WWW",
    "Singleton",
    "LocationsAPIClient"
]


log = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class WWW(metaclass=Singleton):
    __session__ = requests.Session()

    def conn(self):
        return self.__session__


class LocationsAPIClient:

    def __init__(self, home_url: str = None, auth_token: str = None):
        self.home_url = home_url
        self.auth_token = auth_token

    def get_token(self):
        # ToDo: Machine 2 machine login?.
        token = self.auth_token or os.environ.get("TOKKO_AUTH_TOKEN")
        return f"?format=json&api_key={token}"

    def get_api_home(self):
        return self.home_url or os.environ.get("LOCATIONS_API_HOME")

    def get_url(self, method: str, *uri_vars) -> str:
        api_home = self.get_api_home()
        tokko_locations_api_key = self.get_token()
        if uri_vars:
            method = f"{method}/{os.path.join(*uri_vars)}"
        url = os.path.join(api_home, method, tokko_locations_api_key)
        return url

    def fetch(self, method, verb: str = None, data: Union[dict] = None, **options) -> Union[list, dict]:
        verb = verb or "get"
        log.info(f"Fetching method={method}{verb.upper()}")
        headers = options.pop("headers", {})
        url = self.get_url(method, *options.pop("uri_values", []))
        log.debug(url)
        conn = WWW().conn()
        try:
            request = getattr(conn, verb)
            response = request(url, data=data, headers=headers)
            response.raise_for_status()
            json_data = response.json()
            log.debug(json_data)
            data_key = options.pop("data_key", None)
            if data_key:
                return json_data[data_key]
            return json_data
        except (ConnectionError, HTTPError) as error:
            raise APIConnectionError(f"{error}") from error
        except KeyError as error:
            raise DataNotFoundError(f"{error}") from error

    @staticmethod
    def build_method(method):
        return f"api/v1/{method}"

    def countries(self):
        log.info("Retrieving Countries ...")
        _countries = self.fetch(self.build_method("countries"), data_key="objects")
        return list(map(lambda _country: Country(**_country), _countries))

    def country(self, country_id: int):
        log.info(f"Retrieving Country {country_id} ...")
        _country = self.fetch(self.build_method("country"), uri_values=[f"{country_id}"])
        return Country(**_country)

    def state(self, state_id: int):
        log.info(f"Retrieving State #{state_id} ...")
        _state = self.fetch(self.build_method("state"), uri_values=[f"{state_id}"])
        return State(**_state)

    def location(self, location_id: int):
        log.info(f"Retrieving Location #{location_id} ...")
        _location = self.fetch(self.build_method("location"), uri_values=[f"{location_id}"])
        return Location(**_location)

