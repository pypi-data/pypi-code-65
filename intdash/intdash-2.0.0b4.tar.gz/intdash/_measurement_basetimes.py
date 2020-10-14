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
import json

import requests

import intdash
from intdash import timeutils

__all__ = ["MeasurementBasetimes"]


class MeasurementBasetimes(object):
    """基準時刻リソースへのアクセスオブジェクトです。"""

    def __init__(self):
        self.client = None

    def get(self, measurement_uuid, type):
        """基準時刻を取得します。

        Args:
            measurement_uuid (str): 計測のUUID
            type (BasetimeType): 取得対象の基準時刻タイプ

        Returns:
            MeasurementBasetime: 基準時刻オブジェクト
        """
        resp = json.loads(
            self.client._request(
                method="get",
                spath="/api/v1/measurements/{measurement_uuid}/basetimes/{type}".format(
                    measurement_uuid=measurement_uuid, type=type
                ),
            ).text
        )

        return intdash.MeasurementBasetime._from_dict(resp)

    def update(self, measurement_uuid, basetime, type="manual"):
        """基準時刻を作成または更新します。

        Args:
            measurement_uuid (str): 計測のUUID
            basetime (pandas.Timestamp): 設定する基準時刻
            type (BasetimeType): 更新対象の基準時刻タイプ
        """
        data = {"basetime": timeutils.timestamp2str(basetime)}

        self.client._request(
            method="put",
            spath="/api/v1/measurements/{measurement_uuid}/basetimes/{type}".format(
                measurement_uuid=measurement_uuid, type=type
            ),
            json=data,
            code=requests.codes.no_content,
        )

    def delete(self, measurement_uuid, type):
        """基準時刻を削除します。

        Args:
            measurement_uuid (str): 計測のUUID
            type (BasetimeType): 削除対象の基準時刻タイプ
        """
        self.client._request(
            method="delete",
            spath="/api/v1/measurements/{measurement_uuid}/basetimes/{type}".format(
                measurement_uuid=measurement_uuid, type=type
            ),
            code=requests.codes.no_content,
        )

    def list(self, measurement_uuid):
        """基準時刻のリストを取得します。

        Args:
            measurement_uuid (str): 計測のUUID

        Returns:
            list[MeasurementBasetime]: 基準時刻オブジェクトのリスト
        """
        resp = json.loads(
            self.client._request(
                method="get",
                spath="/api/v1/measurements/{measurement_uuid}/basetimes".format(
                    measurement_uuid=measurement_uuid
                ),
            ).text
        )

        return [intdash.MeasurementBasetime._from_dict(item) for item in resp["items"]]
