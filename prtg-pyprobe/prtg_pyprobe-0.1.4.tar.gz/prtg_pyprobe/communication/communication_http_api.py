import json
import logging

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError, ConnectionError
from urllib3.util.retry import Retry


class PRTGHTTPApi(object):
    PROTOCOL_VERSION = 1

    def __init__(self, probe_config, backoff_factor):
        self.probe_config = probe_config
        self.server_uri = f'https://{self.probe_config["prtg_server_ip_dns"]}:{self.probe_config["prtg_server_port"]}'
        self.auth = frozenset(
            [
                ("gid", self.probe_config["probe_gid"]),
                ("key", self.probe_config["probe_access_key_hashed"]),
                ("protocol", self.PROTOCOL_VERSION),
            ]
        )
        self.session = requests.Session()
        self.retry_strategy = Retry(
            total=5,
            backoff_factor=backoff_factor,
            status_forcelist=[400, 429, 500, 502, 503, 504],
            method_whitelist=["POST"],
        )
        self.adapter = HTTPAdapter(max_retries=self.retry_strategy)
        if probe_config["disable_ssl_verification"]:
            logging.info("Disabling verification of PRTG certificate")

    def _send_api_request(self, api_url=None, post_data=None, url_params=None) -> Response:
        self.session.mount("https://", self.adapter)
        try:
            result = self.session.post(
                url=api_url,
                data=post_data,
                params=url_params,
                verify=not self.probe_config["disable_ssl_verification"],
            )
            if result.status_code == 401:
                logging.error("Cannot connect to the PRTG server, have you approved your probe?")
            return result
        except RetryError:
            logging.exception("Max connection retries exceeded, backing off!")
            raise
        except ConnectionError:
            logging.exception("Cannot connect to server, please check your config")
            raise

    def send_announce(self, sensor_definitions: list) -> Response:
        announce_url = self.server_uri + "/probe/announce"
        announce_params = dict(self.auth)
        announce_params["probe_base_interval"] = self.probe_config["probe_base_interval"]
        announce_params["sensors"] = json.dumps(sensor_definitions)
        announce_params["name"] = self.probe_config["probe_name"]
        logging.info(f"Sending Announce request to PRTG Core at {self.server_uri}")
        logging.debug(f"Payload for Announce request to {announce_url} is: {str(announce_params)}")
        return self._send_api_request(api_url=announce_url, post_data=announce_params)

    def get_tasks(self) -> Response:
        tasks_url = self.server_uri + "/probe/tasks"
        logging.info(f"Sending Task request to PRTG Core at {self.server_uri}")
        logging.debug(f"Payload for Task request to {tasks_url} is: {str(dict(self.auth))}")
        return self._send_api_request(api_url=tasks_url, post_data=dict(self.auth))

    def send_data(self, sensor_response_data: list) -> Response:
        data_url = self.server_uri + "/probe/data"
        logging.info(f"Sending Data Request to PRTG Core at {self.server_uri}")
        logging.debug(
            f"Payload for Data request to {data_url} with URL parameters {str(dict(self.auth))} is: "
            f"{str(sensor_response_data)}"
        )
        return self._send_api_request(
            api_url=data_url,
            post_data=json.dumps(sensor_response_data),
            url_params=dict(self.auth),
        )
