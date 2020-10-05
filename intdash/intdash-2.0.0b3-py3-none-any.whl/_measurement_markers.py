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

__all__ = ["MeasurementMarkers"]


class MeasurementMarkers(object):
    """計測マーカーリソースへのアクセスオブジェクトです"""

    def __init__(self):
        self.client = None
        self.version = None

    def create(
        self, measurement_uuid, type, detail, name=None, description=None, tag=None
    ):
        """計測マーカーをサーバーへ作成します。

        Args:
            measurement_uuid (str): 計測UUID
            type (MeasurementMarkerType): 計測マーカー種別 ( ``point`` or ``range`` )
            detail (MeasurementMarkerDetail): 計測マーカーの詳細
            name (str): 計測マーカー名
            description (str): 説明
            tag (dict): タグ情報

        Returns:
            MeasurementMarker: 計測マーカーオブジェクト

        .. note::
            ``detail`` は 指定した ``type`` に応じて以下のオブジェクトを指定ください。

            * ``type`` が ``point`` の場合は、intdash.MeasurementMarkerDetailPoint を指定してください。
            * ``type`` が ``range`` の場合は、intdash.MeasurementMarkerDetailRange を指定してください。

        .. note::
            ``tag`` は、Key(string)とValue(string)のペアのみ登録することができます。

            .. parsed-literal::
                // NG
                {
                    "tagkey" : {
                        "nestKey": "not allowed"
                    }
                }

                // OK
                {
                    "tagkey1" : "ok"
                    "tagkey2" : "ok"
                }
        """

        data = {"detail": detail._to_dict(), "type": type}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if tag:
            data["tag"] = tag

        resp = json.loads(
            self.client._request(
                method="post",
                spath="/api/v1/measurements/{}/markers".format(measurement_uuid),
                json=data,
                code=requests.codes.created,
                version=self.version["create"]["version"],
            ).text
        )

        return intdash.MeasurementMarker._from_dict(resp)

    def get(self, marker_uuid):
        """計測マーカーを取得します。

        Args:
            marker_uuid (str): 取得対象の計測マーカーのUUID

        Returns:
            MeasurementMarker: 計測マーカーオブジェクト
        """

        resp = json.loads(
            self.client._request(
                method="get",
                spath="/api/v1/measurements/markers/{marker_uuid}".format(
                    marker_uuid=marker_uuid
                ),
                version=self.version["get"]["version"],
            ).text
        )

        return intdash.MeasurementMarker._from_dict(resp)

    def update(
        self,
        marker_uuid,
        measurement_uuid=None,
        name=None,
        description=None,
        type=None,
        detail=None,
        tag=None,
    ):
        """計測マーカーを更新します。

        Args:
            marker_uuid (str): 更新対象の計測マーカーのUUID
            measurement_uuid (str): 更新対象の計測マーカーが紐づいている計測のUUID
            type (MeasurementMarkerType): 計測マーカー種別 ( ``point`` or ``range`` )
            detail (MeasurementMarkerDetail): 計測マーカーの詳細
            name (str): 計測マーカー名
            description (str): 説明
            tag (dict): タグ情報

        Returns:
            MeasurementMarker: 計測マーカーオブジェクト

        .. note::
            ``detail`` は 指定した ``type`` に応じて以下のオブジェクトを指定ください。
            ``type`` が ``point`` の場合は、MeasurementMarkerDetailPoint を指定してください。
            ``type`` が ``range`` の場合は、MeasurementMarkerDetailRange を指定してください。

        .. note::
            ``measurement_uuid`` を指定した際、 ``marker_uuid`` の計測マーカーが指定の計測に紐付いていないと更新されません。
        """

        data = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if type:
            data["type"] = type
        if detail:
            data["detail"] = detail._to_dict()
        if tag:
            data["tag"] = tag

        if measurement_uuid:
            path = (
                "/api/v1/measurements/{measurement_uuid}/markers/{marker_uuid}".format(
                    measurement_uuid=measurement_uuid, marker_uuid=marker_uuid
                )
            )

            version = self.version["update_by_measurement"]["version"]
        else:
            path = "/api/v1/measurements/markers/{marker_uuid}".format(
                marker_uuid=marker_uuid
            )
            version = self.version["update_by_marker"]["version"]

        resp = json.loads(
            self.client._request(
                method="put",
                spath=path,
                json=data,
                code=requests.codes.created,
                version=version,
            ).text
        )

        return intdash.MeasurementMarker._from_dict(resp)

    def delete(self, marker_uuid, measurement_uuid=None):
        """計測マーカーをサーバーから削除します。

        Args:
            marker_uuid (str): 削除対象のマーカーのUUID
            measurement_uuid (str): 削除対象の計測マーカーが紐づいている計測のUUID

        .. note::
            ``measurement_uuid`` を指定した際、 ``marker_uuid`` の計測マーカーが指定の計測に紐付いていない場合はエラーになります。
        """
        if measurement_uuid:
            path = (
                "/api/v1/measurements/{measurement_uuid}/markers/{marker_uuid}".format(
                    measurement_uuid=measurement_uuid, marker_uuid=marker_uuid
                )
            )
            version = self.version["delete_by_measurement"]["version"]
        else:
            path = "/api/v1/measurements/markers/{marker_uuid}".format(
                marker_uuid=marker_uuid
            )
            version = self.version["delete_by_marker"]["version"]

        self.client._request(
            method="delete", spath=path, code=requests.codes.created, version=version
        )

    def list(self, measurement_uuid):
        """計測UUIDに紐づくすべての計測マーカーを取得します。

        Args:
            measurement_uuid (str): 計測UUID

        Returns:
            list[MeasurementMarker]: 計測マーカーオブジェクトのリスト
        """

        resp = json.loads(
            self.client._request(
                method="get",
                spath="/api/v1/measurements/{measurement_uuid}/markers".format(
                    measurement_uuid=measurement_uuid
                ),
                version=self.version["list"]["version"],
            ).text
        )

        return [intdash.MeasurementMarker._from_dict(item) for item in resp["items"]]
