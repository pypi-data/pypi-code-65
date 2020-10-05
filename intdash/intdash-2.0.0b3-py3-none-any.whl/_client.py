# Copyright 2020 Aptpod, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""intdashサーバーに対するアクセス API を提供します。
"""

import copy
import json
import sys
import warnings

import requests
from tornado import gen, locks, queues

import intdash
from intdash import __version__, _api_endpoints, protocol

__all__ = ["Client"]

USER_AGENT = "IntdashPythonClient/%s (%d.%d.%d-%s-%d)" % (
    (__version__,) + sys.version_info
)

MINIMUM_API_VERSION = "1.9.0"


class APICompatibilityException(Exception):
    pass


class Client(object):
    """intdash REST サーバーに対するアクセスクライアントです。

    Args:
        url (str): intdash REST API サーバーの URL
        username (str): ユーザー名
        password (str): パスワード
        edge_token (str): エッジトークン
        verify (bool): サーバ証明書の検証を行うかどうか（デフォルトは ``True`` ）

    .. note::
        認証情報として、 **ユーザー名／パスワード** もしくは **エッジトークン** のいずれかが必要です。
    """

    def __init__(self, url, username=None, password=None, edge_token=None, verify=True):
        self.url = url

        self.edge_token = edge_token
        self.username = username
        self.password = password

        self.jwt = None
        self.verify = verify

        self.api_version = None
        self._validate_api_compatibility()

        if username is not None and password is not None:
            self._auth()

    def _request(
        self,
        method,
        spath,
        json=None,
        data=None,
        files=None,
        query=None,
        version=None,
        code=requests.codes.ok,
        headers={},
    ):
        headers["User-Agent"] = USER_AGENT

        if json is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"

        if self.edge_token is not None:
            headers["X-Edge-Token"] = self.edge_token

        elif self.jwt is not None:
            headers["Authorization"] = "Bearer " + self.jwt

        resp = requests.request(
            url=self.url + spath,
            method=method,
            json=json,
            data=data,
            files=files,
            params=query,
            headers=headers,
            verify=self.verify,
        )

        if resp.status_code is not code:
            if version:
                supported = intdash._utils._check_supported(self.api_version, version)
            else:
                supported = True

            if resp.status_code == 404 and not supported:
                resp.reason = (
                    "Called api is not supported. Please check intdash-api version."
                )
            resp.raise_for_status()

        return resp

    #
    # validate intdash-api compatibility
    #
    def _validate_api_compatibility(self):
        resp = requests.request(
            url=self.url + "/api/v1/version", method="get", verify=self.verify
        )

        if resp.status_code is not requests.codes.ok:
            warnings.warn(
                f"intdash-py does not support the version of intdash-API it accesses. It is compatible with API versions {MINIMUM_API_VERSION} or more.",
                UserWarning,
            )
            return

        self.api_version = json.loads(resp.text)["version"]
        if not intdash._utils._check_supported(self.api_version, MINIMUM_API_VERSION):
            warnings.warn(
                f"intdash-py does not support the version of intdash-API it accesses. It is compatible with API versions {MINIMUM_API_VERSION} or more.",
                UserWarning,
            )
            return

    #
    # auth
    #
    def _auth(self):
        if self.edge_token is not None:
            return

        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json; charset=utf-8",
        }

        data = {"username": self.username, "password": self.password}

        resp = requests.request(
            url=self.url + "/api/v1/authn",
            method="post",
            json=data,
            headers=headers,
            verify=self.verify,
        )

        if resp.status_code is not requests.codes.ok:
            resp.raise_for_status()

        self.jwt = json.loads(resp.text)["token"]

    #
    # intdash services
    #

    @property
    def edges(self):
        """intdash.Edges: エッジリソースへのアクセスオブジェクト"""
        edges = intdash.Edges()
        edges.client = self
        return edges

    @property
    def measurements(self):
        """intdash.Measurements: 計測リソースへのアクセスオブジェクト"""
        measurements = intdash.Measurements()
        measurements.client = self
        measurements.version = _api_endpoints.API_VERSIONS["measurements"]

        return measurements

    @property
    def measurement_basetimes(self):
        """intdash.MeasurementBasetimes: 基準時刻リソースへのアクセスオブジェクト"""
        measurement_basetimes = intdash.MeasurementBasetimes()
        measurement_basetimes.client = self
        return measurement_basetimes

    @property
    def measurement_markers(self):
        """intdash.MeasurementMarkers: 計測マーカーリソースへのアクセスオブジェクト"""
        measurement_markers = intdash.MeasurementMarkers()
        measurement_markers.client = self
        measurement_markers.version = _api_endpoints.API_VERSIONS["measurement_markers"]

        return measurement_markers

    @property
    def units(self):
        """intdash.Units: 時系列データ(ユニット形式)へのアクセスオブジェクト"""
        units = intdash.Units()
        units.client = self
        return units

    def connect_websocket(self, flush_interval=0.01, auto_reconnect=False):
        """intdash WebSocket エンドポイントへ接続します。

        Args:
            flush_interval (float): 秒単位のフラッシュ間隔
            auto_reconnect (bool): 自動再接続フラグ

        Returns:
            intdash.WebSocketConn: WebSocketコネクション
        """
        web_socket_conn = intdash.WebSocketConn()
        web_socket_conn._init(
            client=copy.deepcopy(self),
            flush_interval=flush_interval,
            auto_reconnect=auto_reconnect,
        )
        return web_socket_conn

    @property
    def data_points(self):
        """intdash.DataPoints: 時系列データ(データポイント形式)へのアクセスオブジェクト"""

        data_points = intdash.DataPoints()
        data_points.client = self
        return data_points

    @property
    def signals(self):
        """intdash.Signals: 信号定義リソースへのアクセスオブジェクト"""
        signals = intdash.Signals()
        signals.client = self
        return signals

    @property
    def captures(self):
        """intdash.Captures: キャプチャリソースへのアクセスオブジェクト"""
        captures = intdash.Captures()
        captures.client = self
        return captures
