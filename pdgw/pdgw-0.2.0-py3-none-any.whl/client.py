import json
from typing import List

import urllib3

from .http import Http
from .mqtt import Mqtt


class Client:

    pool = urllib3.PoolManager(
        retries=urllib3.Retry(connect=3, read=2, redirect=2, status=0))

    def __init__(self, *,
                 org_id: str,
                 app_id: str,
                 api_key: str,
                 beacon_host="beacon.scaleplan.net",
                 beacon_port=9000):
        self.org_id = org_id
        self.app_id = app_id
        self.api_key = api_key
        self.beacon_addr = beacon_host
        self.http_url = ""
        self.auth_header = f"Bearer {beacon_host}"
        self.beacon_url = f"http://{beacon_host}:{beacon_port}/v0/info"
        self._server = None
        self._http = None
        self._mqtt = None
        self.connect_beacon()


    @property
    def http(self) -> Http:
        return self._http

    @property
    def mqtt(self) -> Mqtt:
        return self._mqtt

    def connect_beacon(self) -> (dict, List):
        body = json.dumps({
            "org_id": self.org_id,
            "app_id": self.app_id,
        })
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
        }
        r = self.pool.request("POST", self.beacon_url, headers=headers, body=body)
        text = r.data.decode("utf-8")
        if r.status != 200:
            raise ClientError("Could not receive beacon info %s" % text)
        resp_json = json.loads(text)
        self._server = resp_json["server"]
        self.process_features(resp_json["features"])

    def process_features(self, features):
        http_feature = features.get("http")
        if http_feature is not None and len(http_feature) > 0:
            # TODO: check whether JSON is supported
            http_feature = http_feature[0]
            proto = "https" if http_feature.get("ssl") else "http"
            host = http_feature.get("host")
            if host is None:
                raise ClientError("Invalid HTTP feature: host is missing")
            port = http_feature.get("port")
            if port is None:
                raise ClientError("Invalid HTTP feature: port is missing")
            base_url = f"{proto}://{host}:{port}"
            self._http = Http(self.pool, base_url)
            return

        mqtt_feature = features.get("mqtt")
        if mqtt_feature is not None and len(mqtt_feature) > 0:
            # TODO: check whether JSON is supported
            mqtt_feature = mqtt_feature[0]
            host = mqtt_feature.get("host")
            if host is None:
                raise ClientError("Invalid MQTT feature: host is missing")
            port = mqtt_feature.get("port")
            if port is None:
                raise ClientError("Invalid MQTT feature: port is missing")
            self._mqtt = Mqtt(host=host, port=port)
            return

        raise ClientError("HTTP and MQTT are not supported by the gateway.")


class ClientError(Exception):
    pass