from urllib.parse import urlencode
from typing import Union, List
import logging
import os

import requests

from tokko_locations_client.models import Country, State, Location
from requests.exceptions import HTTPError, ConnectionError
from tokko_locations_client.helpers import Extends
from tokko_locations_client.exceptions import (
    APIConnectionError,
    DataNotFoundError,
    APIHomeNotFoundError,
)


__all__ = ["WWW", "Singleton", "LocationsAPIClient"]


log = logging.getLogger(__name__)
IdType = Union[str, int]


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
        return self.auth_token or os.environ.get("TOKKO_AUTH_TOKEN")

    def get_api_home(self):
        self.home_url = self.home_url or os.environ.get("LOCATIONS_API_HOME")
        if not self.home_url:
            raise APIHomeNotFoundError()
        return self.home_url

    def get_uri_vars(self, res_format: str = None, lang: str = None, **uri_vars) -> str:
        uri_vars.update({
            "format": res_format or "json",
            "lang": lang or "es_ar",
            "api_key": self.get_token()
        })
        return urlencode(uri_vars)

    def get_url(self, method: str, *uri_args, **uri_vars) -> str:
        api_home = self.get_api_home()
        if uri_args:
            method = f"{method}/{os.path.join(*uri_args)}"
        url = os.path.join(api_home, method)
        return f"{url}?{self.get_uri_vars(**uri_vars)}"

    def fetch(self, method, verb: str = None, data: Union[dict] = None, **options) -> Union[list, dict]:
        verb = verb or "get"
        log.info(f"Fetching method={method}{verb.upper()}")
        headers = options.pop("headers", {})
        url = self.get_url(
            method,
            *options.pop("uri_args", []),
            **options.pop("uri_vars", {})
        )
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

    @staticmethod
    def get_id_from_uri(uri):
        return int([blk for blk in uri.split("/") if blk][-1])

    def country(self, country_id: IdType) -> Country:
        if isinstance(country_id, str):
            country_id = self.get_id_from_uri(country_id)
        log.info(f"Retrieving Country {country_id} ...")
        _country = self.fetch(
            self.build_method("country"), uri_args=[f"{country_id}"]
        )
        return Country(**_country)

    def state(self, state_id: IdType) -> State:
        if isinstance(state_id, str):
            state_id = self.get_id_from_uri(state_id)
        log.info(f"Retrieving State #{state_id} ...")
        _state = self.fetch(self.build_method("state"), uri_args=[f"{state_id}"])
        return State(**_state)

    @Extends("state", resolve_with_method="state", target_class=str)
    def location(self, location_id: IdType) -> Location:
        if isinstance(location_id, str):
            location_id = self.get_id_from_uri(location_id)
        log.info(f"Retrieving Location #{location_id} ...")
        _location = self.fetch(
            self.build_method("location"), uri_args=[f"{location_id}"]
        )
        return Location(**_location)

    def location_quick_search(self, keyword: str) -> List[Location]:
        log.info(f"Searching for location that name match with #{keyword} ...")
        _locations = self.fetch(
            self.build_method("location"),
            data_key="objects",
            uri_args=["quicksearch"],
            uri_vars={"q": keyword}
        )
        return [
            Location(**location)
            for location in _locations
        ]
