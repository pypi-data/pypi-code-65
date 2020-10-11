import json
import re
import time
from typing import Optional, List

import requests
from requests.auth import HTTPBasicAuth

from .api_endpoints import get_api_endpoint
from .request_headers import get_request_headers


class ApiConnection:
    def __init__(self, id_user: str, key_pass: str, sleep=0.5, auth_type_user=False):
        self.id_user: str = id_user
        self.key_pass: str = key_pass
        self.sleep: float = sleep
        self.auth_type_user: bool = auth_type_user

        dc_auth_params = {}
        if auth_type_user:
            dc_auth_params["root"] = 1

        response = requests.request(
            url=get_api_endpoint(endpoint='session'),
            method='post',
            params=dc_auth_params,
            auth=HTTPBasicAuth(id_user, key_pass)
        )
        response_json = json.loads(response.text)
        self.token: str = response_json["token"]

    def dc_request(
            self, url: str, method: str,
            content_type: Optional[str] = 'json', filters: Optional[dict] = None, **kwargs
    ) -> requests.Response:
        encoded_filters = {}
        if filters:
            for key, value in filters.items():
                encoded_filters['q[' + key + ']'] = value

        response = requests.request(
            url=url,
            method=method.upper(),
            headers=get_request_headers(self.token, content_type),
            params=encoded_filters,
            **kwargs
        )
        response.raise_for_status()

        return response

    def get_paginated_data(
            self, url: str, method: str,
            filters: Optional[dict] = None, per_page: int = 200, page: Optional[int] = None, page_limit=None
    ) -> List[dict]:
        results = []

        if page:
            url = f"{url}?per_page={per_page}&page={page}"
            response = self.dc_request(url, method, filters=filters)
            return response.json()

        page = 1
        while True:
            url = f"{url}?per_page={per_page}&page={page}"
            response = self.dc_request(url, method, filters=filters)
            results.extend(response.json())

            pages = re.findall("(?<=rel=\\')(.*?)(?=\\')", response.headers.get("link", ""))
            has_next = True if "next" in pages else False
            if not has_next or (page_limit and page == page_limit):
                break
            time.sleep(self.sleep)  # we don't want to overload DC database.
            page += 1

        return results
