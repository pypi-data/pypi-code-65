from functools import wraps
import http
import json
import time
import requests


class CallFailure(Exception):
    pass

class HttpException(Exception):
    pass

class BadRequest(HttpException):
    pass

class Unauthenticated(HttpException):
    pass

class Forbidden(HttpException):
    pass

class Decorators:

    """
    Authentication
    """

    MAX_AUTH_RETRIES = 1

    @staticmethod
    def authenticated(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for attempt in range(0, Decorators.MAX_AUTH_RETRIES):
                # Obtain token if necessary
                if self.api_key is None:
                    if self.refresh_token is None:
                        self.auth_core_anonymous_get_dict()
                    elif self.access_token is None:
                        self.auth_core_refresh_post_dict()

                # Make a call
                try:
                    return func(self, *args, **kwargs)
                except Unauthenticated as _:
                    # Wipe previously issued access token
                    self.access_token = None
                    self.expires_at = None
        return wrapper

    """
    Retries    
    """

    MAX_CALL_RETRIES = 3
    DELAY_IN_SECONDS = 1.0

    @staticmethod
    def retriable(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Perform a number of attempts
            for attempt in range(0, Decorators.MAX_CALL_RETRIES):
                # Make a call
                try:
                    result = func(self, *args, **kwargs)
                    return result
                except CallFailure as _:
                    pass
                # Wait for a bit
                time.sleep(Decorators.DELAY_IN_SECONDS)

            # Fail the call if nothing helps
            raise CallFailure()
        return wrapper


class Api:

    BASE_URL = "https://api.blobhub.io"
    BASE_VERSION = "v1"

    def __init__(self, base_url=None, base_version=None, api_key=None):
        self.base_url = base_url if base_url is not None else self.BASE_URL
        self.base_version = base_version if base_version is not None else self.BASE_VERSION
        self.api_key = api_key
        self.refresh_token = None
        self.access_token = None
        self.expires_at = None

    """
    API methods 
    """

    @Decorators.retriable
    @Decorators.authenticated
    def blobs_blob_id_org_id_get_dict(self, org_id, blob_id):
        path = "blobs/{}/{}".format(org_id, blob_id)
        response, _ = self.request(method="GET", path=path)
        return response["blob"]

    @Decorators.retriable
    @Decorators.authenticated
    def blobs_blob_id_org_id_revisions_get_dict(self, org_id, blob_id):
        path = "blobs/{}/{}/revisions".format(org_id, blob_id)
        response, _ = self.request(method="GET", path=path)
        return response["revisions"]

    @Decorators.retriable
    @Decorators.authenticated
    def revisions_revision_id_data_command_post(self, revision_id, body: dict, data=None, headers=None):
        path = "revisions/{}/data/command".format(revision_id)
        response_body, response_data = self.request(method="POST", path=path, body=body, data=data, headers=headers)
        return response_body, response_data

    @Decorators.retriable
    @Decorators.authenticated
    def revisions_revision_id_data_query_post(self, revision_id, body: dict, data=None, headers=None):
        path = "revisions/{}/data/query".format(revision_id)
        response_body, response_data = self.request(method="POST", path=path, body=body, data=data, headers=headers)
        return response_body, response_data

    @Decorators.retriable
    def auth_core_anonymous_get_dict(self):
        path = "auth/core/anonymous"
        response, _ = self.request(method="GET", path=path, auth=False)
        self.refresh_token = response["refresh_token"]
        self.access_token = response["access_token"]

    @Decorators.retriable
    def auth_core_refresh_post_dict(self):
        try:
            # Attempt to refresh access token
            path = "auth/core/refresh"
            body = {"refresh_token": self.refresh_token}
            response, _ = self.request(method="POST", path=path, body=body, auth=False)
            self.access_token = response["access_token"]
        except Unauthenticated as _:
            # Obtain new set of anonymous tokens (including refresh token)
            self.auth_core_anonymous_get_dict()

    """
    Core Requests
    """

    def request(self, method, path, body=None, data=None, auth=True, headers=None):
        try:
            # Prepare and execute request
            url = "{}/{}/{}".format(self.base_url, self.base_version, path)
            if headers is None:
                headers = {}
            if data is None:
                headers["Content-Type"] = "application/json"
                data = body
            else:
                headers["Content-Type"] = "application/octet-stream"
                headers["X-Request-Body"] = json.dumps(body)
            if isinstance(data, dict):
                data = json.dumps(data)
            if auth:
                if self.access_token is not None:
                    headers["Authorization"] = "Bearer {}".format(self.access_token)
                elif self.api_key is not None:
                    headers["X-API-Key"] = self.api_key
                else:
                    raise Unauthenticated()

            response = requests.request(method=method, url=url, headers=headers, data=data)

            # Analyze response for recoverable failures
            if 0 == response.status_code or response.status_code >= 500:
                raise CallFailure()
            if http.HTTPStatus.BAD_REQUEST == response.status_code:
                raise BadRequest()
            if http.HTTPStatus.UNAUTHORIZED == response.status_code:
                raise Unauthenticated()
            if http.HTTPStatus.FORBIDDEN == response.status_code:
                raise Forbidden()

            # Prepare response
            if "application/json" == response.headers["Content-Type"]:
                response_body = response.json()
                return response_body, None
            elif "application/octet-stream" == response.headers["Content-Type"]:
                response_body = json.loads(response.headers.get("X-Response-Body", "{}"))
                response_data = response.content
                return response_body, response_data
            else:
                raise Exception("invalid_response_content_type")
        except HttpException as e:
            raise e
        except Exception as _:
            raise CallFailure()

    @staticmethod
    def is_response_successful(response):
        return "success" == response["status"]

    @staticmethod
    def _enable_detailed_requests_logging():
        # Client logging level
        import http.client as http_client
        http_client.HTTPConnection.debuglevel = 1

        # Logging initialization
        import logging
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
