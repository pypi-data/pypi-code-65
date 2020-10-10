import sys
import os
import requests
from requests.exceptions import ConnectionError
import click

from . import utils
from . import credentials
from .env import BASE_URL


def _parse_response(response_obj):
    # "no content" response
    if not response_obj.headers.get('Content-Type') and \
            response_obj.status_code in [201, 202, 204]:
        return None

    data = {}
    try:
        data = response_obj.json()
    except Exception:
        click.echo("ERROR: Malformed data returned")
        sys.exit()

    data["status_code"] = response_obj.status_code

    if int(data["status_code"] / 100) != 2:
        error = data.get("errors", [{
            "id": "invalid_request",
            "message": "Cannot process request"
        }])[0]

        click.echo(click.style("\nFAILED", fg="red"), nl=False)
        click.echo(" (status code {code}):".format(
            code=data["status_code"]))

        click.echo(utils.to_json(error))
        sys.exit()

    return data.get("data", {})


def bearer_token():
    token = os.getenv("TOKEN")
    if not token:
        credentials.config()
    token = credentials.decrypt(token)
    return {"Authorization": "Bearer {token}".format(token=token)}


class api:

    @staticmethod
    def get(endpoint, **kwargs):
        url = "{url}{endpoint}".format(url=BASE_URL, endpoint=endpoint)
        if "headers" not in kwargs:
            kwargs["headers"] = bearer_token()
        try:
            r = requests.get(url, **kwargs)
            return _parse_response(r)
        except ConnectionError:
            click.echo("ERROR: Cannot establish connection to Tradologics")
            sys.exit()

    @staticmethod
    def post(endpoint, **kwargs):
        try:
            url = "{url}{endpoint}".format(url=BASE_URL, endpoint=endpoint)
            if "headers" not in kwargs:
                kwargs["headers"] = bearer_token()
            r = requests.post(url, **kwargs)
            return _parse_response(r)
        except ConnectionError:
            click.echo("ERROR: Cannot establish connection to Tradologics")
            sys.exit()

    @staticmethod
    def patch(endpoint, **kwargs):
        try:
            url = "{url}{endpoint}".format(url=BASE_URL, endpoint=endpoint)
            if "headers" not in kwargs:
                kwargs["headers"] = bearer_token()
            r = requests.patch(url, **kwargs)
            return _parse_response(r)
        except ConnectionError:
            click.echo("ERROR: Cannot establish connection to Tradologics")
            sys.exit()

    @staticmethod
    def put(endpoint, **kwargs):
        try:
            url = "{url}{endpoint}".format(url=BASE_URL, endpoint=endpoint)
            if "headers" not in kwargs:
                kwargs["headers"] = bearer_token()
            r = requests.put(url, **kwargs)
            return _parse_response(r)
        except ConnectionError:
            click.echo("ERROR: Cannot establish connection to Tradologics")
            sys.exit()

    @staticmethod
    def delete(endpoint, **kwargs):
        try:
            url = "{url}{endpoint}".format(url=BASE_URL, endpoint=endpoint)
            if "headers" not in kwargs:
                kwargs["headers"] = bearer_token()
            r = requests.delete(url, **kwargs)
            return _parse_response(r)
        except ConnectionError:
            click.echo("ERROR: Cannot establish connection to Tradologics")
            sys.exit()

    @staticmethod
    def options(endpoint, **kwargs):
        try:
            url = "{url}{endpoint}".format(url=BASE_URL, endpoint=endpoint)
            if "headers" not in kwargs:
                kwargs["headers"] = bearer_token()
            r = requests.options(url, **kwargs)
            return _parse_response(r)
        except ConnectionError:
            click.echo("ERROR: Cannot establish connection to Tradologics")
            sys.exit()
