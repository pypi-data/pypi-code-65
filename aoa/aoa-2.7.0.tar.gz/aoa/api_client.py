from __future__ import absolute_import

import json
import os
import yaml
import logging
import requests
from requests.auth import AuthBase
from typing import List, Dict
from base64 import b64encode


class AoaClient(object):
    def __init__(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.project_id = None
        self.auth = None, None
        self.aoa_url = None
        self.s3_bucket = None

        self.__parse_aoa_config(**kwargs)

    def __parse_yaml(self, yaml_path: str):
        with open(yaml_path, "r") as handle:
            conf = yaml.safe_load(handle)
        self.__parse_kwargs(**conf)

    def __parse_kwargs(self, **kwargs):
        self.aoa_url = kwargs.get("aoa_url", self.aoa_url)

        if "auth_mode" in kwargs:
            auth_mode = kwargs["auth_mode"]
            if auth_mode == "basic":
                if "aoa_credentials" in kwargs:
                    self.auth = AoaAuth(kwargs["aoa_credentials"])

                if "auth_user" in kwargs and "auth_pass" in kwargs:
                    credentials = b64encode("{}:{}".format(kwargs["auth_user"], kwargs["auth_pass"]).encode()).decode()
                    self.auth = AoaAuth(credentials)

            elif auth_mode == "kerberos":
                from requests_kerberos import HTTPKerberosAuth, OPTIONAL
                self.auth=HTTPKerberosAuth(mutual_authentication=OPTIONAL)

            else:
                raise Exception("Auth mode: {} not supported.".format(auth_mode))

        if "verify_connection" in kwargs:
            self.verify_aoa_connection = kwargs["verify_connection"]

    def __parse_env_variables(self):
        self.aoa_url = os.environ.get("AOA_URL", self.aoa_url)

        auth_mode = os.environ.get("AOA_API_AUTH_MODE")

        if auth_mode == "basic":
            if "AOA_API_AUTH_USER" in os.environ and "AOA_API_AUTH_PASS" in os.environ:
                credentials = b64encode("{}:{}".format(os.environ["AOA_API_AUTH_USER"],
                                                       os.environ["AOA_API_AUTH_PASS"]).encode()).decode()
                self.auth = AoaAuth(credentials)

            elif auth_mode == "kerberos":
                from requests_kerberos import HTTPKerberosAuth, OPTIONAL
                self.auth=HTTPKerberosAuth(mutual_authentication=OPTIONAL)

            else:
                raise Exception("Auth mode: {} not supported.".format(auth_mode))

    def set_project_id(self, project_id: str):
        """
        set project id

        Parameters:
           project_id (str): project id(uuid)
        """
        self.project_id = project_id

    def get_current_project(self):
        """
        get project id

        Return:
           project_id (str): project id(uuid)
        """
        return self.project_id

    def __parse_aoa_config(self, **kwargs):
        if "config_file" in kwargs:
            self.__parse_yaml(kwargs['config_file'])
        else:
            from pathlib import Path
            config_file = "{}/.aoa/config.yaml".format(Path.home())
            if os.path.isfile(config_file):
                self.__parse_yaml(config_file)

        self.__parse_env_variables()
        self.__parse_kwargs(**kwargs)

    def select_header_accept(self, accepts: List[str]):
        """
        converts list of header into a string

        Return:
            (str): request header
        """
        if not accepts:
            return
        accepts = [x.lower() for x in accepts]
        if 'application/json' in accepts:
            return 'application/json'
        else:
            return ', '.join(accepts)

    def get_request(self, path, header_params: Dict[str, str], query_params: Dict[str, str]):
        """
        wrapper for get request

        Parameters:
           path (str): url
           header_params (dict): header parameters
           query_params (dict): query parameters

        Returns:
            dict for resources, str for errors, None for 404
        Raise:
            raises HTTPError in case of error status code other than 404
        """

        resp = requests.get(
            url=self.__strip_url(self.aoa_url) + path,
            auth=self.auth,
            headers=header_params,
            params=query_params
        )

        if resp.status_code == 404:
            return None

        resp.raise_for_status()

        try:
            return resp.json()
        except ValueError:
            return resp.text

    def post_request(self, path, header_params: Dict[str, str], query_params: Dict[str, str], body: Dict[str, str]):
        """
        wrapper for post request

        Parameters:
           path (str): url
           header_params (dict): header parameters
           query_params (dict): query parameters
           body (dict): request body

        Returns:
            dict for resources, str for errors
        Raise:
            raises HTTPError in case of error status code
        """
        resp = requests.post(
            url=self.__strip_url(self.aoa_url) + path,
            auth=self.auth,
            headers=header_params,
            params=query_params,
            data=json.dumps(body)
        )

        resp.raise_for_status()

        try:
            return resp.json()
        except ValueError:
            return resp.text

    def put_request(self, path, header_params: Dict[str, str], query_params: Dict[str, str], body: Dict[str, str]):
        """
        wrapper for put request

        Parameters:
           path (str): url
           header_params (dict): header parameters
           query_params (dict): query parameters
           body (dict): request body

        Returns:
            dict for resources, str for errors
        Raise:
            raises HTTPError in case of error status code
        """
        resp = requests.put(
            url=self.__strip_url(self.aoa_url) + path,
            auth=self.auth,
            headers=header_params,
            params=query_params,
            data=json.dumps(body)
        )

        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def __strip_url(self, url):
        return url.rstrip('/')


class AoaAuth(AuthBase):
    def __init__(self, aoa_credentials):
        self.aoa_credentials = aoa_credentials

    def __call__(self, r):
        r.headers['Authorization'] = "Basic {}".format(self.aoa_credentials)
        return r
