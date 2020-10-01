import copy
import json
import logging
import random
import string
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import click
import requests


def rblob(code, status, message, results=[]):
    """
    Response Blob (rblob) standardize the return of the nominode cli response
        validate codes, status

    :param code: examples (404, 422, 200, 203, 405) etc
    :param status: short status ( typically success, failure)
    :param message: Detailed message
    :param results: If returns any rows or values.  Should be json results
    :return: string of json with all response components
    """
    response = {"code": code, "status": status, "message": message, "results": results}

    return json.dumps(response)


def masked_copy(
    obj: Dict[str, Any], keys: List[str] = None
) -> Union[Dict[str, Any], Any]:
    """
    Masks object with a given list of keys.

    :param obj:
    :type obj: dict
    :param keys: A list of keys to mask the copy.
    :type keys: list[str]
    :return: Masked dictionary
    :rtype: dict
    """
    _obj = copy.deepcopy(obj)

    if keys is None:
        return _obj

    if isinstance(keys, str):
        mask_keys = {keys}.intersection(_obj)

    else:
        mask_keys = set(keys).intersection(_obj)

    return {key: value for key, value in _obj.items() if key in mask_keys}


def omit_copy(
    obj: Dict[str, Any], keys: Optional[List[str]] = None
) -> Union[Dict[str, Any], Any]:
    """
    Omits keys from an object from a list of keys.

    :param obj:
    :type obj: dict
    :param keys: A list of keys to omit from the copy.
    :type keys: list[str]
    :return: Filtered dictionary
    :rtype: dict
    """
    _obj = copy.deepcopy(obj)

    if keys is None:
        return _obj

    if isinstance(keys, str):
        mask_keys = {keys}.symmetric_difference(_obj)

    else:
        mask_keys = set(keys).symmetric_difference(_obj)

    return {key: value for key, value in _obj.items() if key in mask_keys}


def exclude_keys(keys: List[str], obj: Dict, parent: str = "") -> Dict:
    new_dict = {}
    for key, value in obj.items():
        resolved_key = f"{parent}.{key}" if parent else key
        if resolved_key not in keys:
            if isinstance(value, dict):
                new_dict[key] = exclude_keys(keys, value, parent=resolved_key)
            elif isinstance(value, list):
                new_dict[key] = [
                    exclude_keys(keys, val, parent=resolved_key) for val in value
                ]
            else:
                new_dict[key] = obj[key]
    return new_dict


def get_nested_value(source_dictionary, key_list):
    for k in key_list:
        source_dictionary = source_dictionary[k]
    return source_dictionary


def create_nested_dic(key_list, value):
    for i, k in enumerate(reversed(key_list)):
        if i == 0:
            x = {k: value}
        else:
            x = {k: x}
    return x


def generate_random(string_length):
    return "".join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(string_length)
    )


class NominodeSession(requests.Session):
    def __init__(self, prefix_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.logger = logging.getLogger("nominode.session")

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)
        self.logger.debug(f"Request {method}:{url}")
        resp = super().request(method, url, *args, **kwargs)
        self.check_response(resp)
        return resp

    def check_response(self, resp):
        if not resp.ok and resp.status_code != 404:
            try:
                reply_data = resp.json()
                print(reply_data, resp.url)
                if resp.status_code == 401:
                    self.logger.error(f"Check secret key is valid\n\t\t {reply_data}")
                elif resp.status_code == 403:
                    self.logger.error(f"Check user permissions\n\t\t {reply_data}")
                else:
                    self.logger.error(f"Error from Nominode: {reply_data['status']}")
            except json.JSONDecodeError:
                self.logger.error(
                    f"Error {resp.status_code} while communicating with Nominode : {resp.text}"
                )
            raise click.Abort
