import json
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError


def external_api_proxy(func):
    """Handle external service API errors."""

    def func_wrapper(*args, **kwargs):
        error = None
        response = {"OK": True}
        try:
            func_response = func(*args, **kwargs)
            response["code"] = func_response.status_code
            response["data"] = func_response.json()
            if response["code"] >= 300:
                error = "nook"

        except json.JSONDecodeError as err:
            error = "cant_parse_json_error"
            response["data"] = func_response.text.strip()

        except (
            ConnectionError,
            requests.exceptions.RequestException,
            requests.exceptions.Timeout
        ) as err:
            error = "connection_error"
            response["data"] = str(err)

        if error:
            response["OK"] = False
            response["error"] = error
        return response
    return func_wrapper


class CommonAPIClient:
    """ API client which expects JSON response.
    """
    def __init__(self, retries=5, backoff_factor=0.1, retry_on_codes=(500, 502, 503, 504)):
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=retry_on_codes,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session = requests.Session()
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    @external_api_proxy
    def do_request(
        self,
        method: str,
        url: str,
        timeout: int = 10,
        headers: dict = None,
        payload: dict = None,
        basic: bool = None):
        options = {"url": url, "timeout": timeout}
        headers and options.update({"headers": headers})

        if payload:
            if method == "GET":
                options["params"] = payload
            elif method in ["POST", "PUT", "PATCH"] and payload:
                options["json"] = payload
        if basic:
            options["auth"] = basic
        response = getattr(self.session, method.lower())(**options)
        return response

    def get(self, url, **kwargs):
        return self.do_request(method="GET", url=url, **kwargs)

    def post(self, url, **kwargs):
        return self.do_request(method="POST", url=url, **kwargs)
