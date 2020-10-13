import dataclasses
import json
from typing import Optional

import requests
import requests.auth
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from bouncer_insight import events


API_URL = 'https://api.getbouncer.com'
SANDBOX_URL = 'https://sandbox.api.getbouncer.com'
EVENTS_ADD_PATH = "/insight/v1/event/add"


def _requests_retry_session(
    retries=3,
    backoff_factor=0.05,
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class Client(object):

    def __init__(self, api_key, base_url=API_URL, timeout=2.0, retries=3, exp_backoff=0.05):
        """Initialize the client.
        Args:
            api_key: The API key associated with your Bouncer Insight account
            base_url: Base URL for Bouncer Insight. Defaults to 'https://api.getbouncer.com'.
            timeout: Number of seconds to wait before timing out each request. Defaults
                to 2 seconds.
            retries: Number of retries to issue on a failed request
            exp_backoff: Backoff factor for each subsequent retry.
                The nth retry will back off (2 ** (n - 1)) * exp_backoff
        """

        self.session = _requests_retry_session(retries, backoff_factor=exp_backoff)
        self.api_key = api_key
        self.url = base_url
        self.timeout_seconds = timeout

    def _send_event(self, event_type: str, event_body: dict, timeout_seconds: Optional[int] = None):
        """Notifies Bouncer Insight of a user event

        Args:
            event_type (str): The name of the event type (e.g. 'user_login')
            event_body (dict): A dict representation of the event body.
            timeout_seconds (int): The timeout for this call. Overrides the default client's timeout_seconds

        Raises:
            ApiException

        Returns:
            Response: if the call succeeded, otherwise
        """
        headers = {
            'Content-type': 'application/json',
            'Accept': '*/*',
            'Authorization': 'Bearer ' + self.api_key
        }

        event_body['event'] = event_type

        if timeout_seconds is None:
            timeout_seconds = self.timeout_seconds

        try:
            response = self.session.post(
                self.url + EVENTS_ADD_PATH,
                data=json.dumps(event_body),
                headers=headers,
                timeout=timeout_seconds
            )
            return Response(response)
        except requests.exceptions.RequestException as e:
            raise ApiException(str(e), self.url + EVENTS_ADD_PATH)

    def send_login_event(self, login_event: events.LoginEvent):
        """Sends a user login event to Bouncer Insight

        Raises:
            TypeError
            ApiException

        Returns:
            Response: if the call succeeded, otherwise
        """
        if not isinstance(login_event, events.LoginEvent):
            raise TypeError(
                "Expected type LoginEvent, got {}".format(
                    type(login_event).__name__)
            )
        return self._send_event('user_login', dataclasses.asdict(login_event))

    def send_user_create_event(self, user_create_event: events.UserCreateEvent):
        """Sends a user login event to Bouncer Insight

        Raises:
            ApiException

        Returns:
            Response: if the call succeeded, otherwise
        """
        if not isinstance(user_create_event, events.UserCreateEvent):
            raise TypeError(
                "Expected type UserCreateEvent, got {}".format(
                    type(user_create_event).__name__)
            )
        return self._send_event('user_create', dataclasses.asdict(user_create_event))

    def send_user_update_event(self, user_update_event: events.UserUpdateEvent):
        """Sends a user login event to Bouncer Insight

        Raises:
            ApiException

        Returns:
            Response: if the call succeeded, otherwise
        """
        if not isinstance(user_update_event, events.UserUpdateEvent):
            raise TypeError(
                "Expected type UserUpdateEvent, got {}".format(
                    type(user_update_event).__name__)
            )
        return self._send_event('user_update', dataclasses.asdict(user_update_event))

    def send_payment_method_add(self, payment_method_add: events.PaymentMethodAddEvent):
        """Sends a user login event to Bouncer Insight

        Raises:
            ApiException

        Returns:
            Response: if the call succeeded, otherwise
        """
        if not isinstance(payment_method_add, events.PaymentMethodAddEvent):
            raise TypeError(
                "Expected type PaymentMethodAddEvent, got {}".format(
                    type(payment_method_add).__name__)
            )
        return self._send_event('payment_method_add', dataclasses.asdict(payment_method_add))


class Response(object):

    def __init__(self, http_response):
        """
        Raises ApiException on a failed Bouncer Insight request
        """
        self.success = 300 > http_response.status_code >= 200
        self.http_status_code = http_response.status_code
        self.url = http_response.url

        if self.http_status_code < 200 or self.http_status_code >= 300:
            raise ApiException(
                'Error occurred on url={0} status_code={1}'.format(self.url, self.http_status_code),
                url=self.url,
                http_status_code=self.http_status_code,
            )


class ApiException(Exception):
    def __init__(self, message, url, http_status_code=None):
        Exception.__init__(self, message)

        self.url = url
        self.http_status_code = http_status_code
