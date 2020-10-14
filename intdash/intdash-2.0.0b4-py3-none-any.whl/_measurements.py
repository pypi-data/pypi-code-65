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
from debtcollector import removals

import intdash
from intdash import timeutils

__all__ = ["Measurements"]


class Measurements(object):
    """計測リソースへのアクセスオブジェクトです。"""

    def __init__(self):
        self.client = None
        self.version = None

    def create(
        self,
        edge_uuid,
        basetime,
        basetime_type="manual",
        name="",
        description="",
        protect=False,
    ):
        """計測をサーバーへ作成します。

        Args:
            edge_uuid (str): エッジのUUID
            basetime (pandas.Timestamp): 基準時刻
            basetime_type (BasetimeType): 基準時刻タイプ
            name (str): 計測名
            description (str): 説明
            protect (bool): 保護要否

        Returns:
            Measurement: 作成された計測オブジェクト

        .. note::
            計測の保護を解除する権限を持たないユーザーの場合、
            保護された計測を作成することはできますが、
            保護された計測を削除することはできません。
            また、計測を保護する権限を持たないユーザーの場合、
            保護されていない計測を、後から保護状態にすることはできません。
        """
        data = {
            "name": name,
            "edge_uuid": edge_uuid,
            "description": description,
            "basetime_type": str(basetime_type),
            "basetime": timeutils.timestamp2str(basetime),
            "protected": protect,
        }

        resp = json.loads(
            self.client._request(
                method="post",
                spath="/api/v1/measurements",
                json=data,
                code=requests.codes.created,
            ).text
        )

        return intdash.Measurement._from_dict(resp)

    def get(self, uuid=None, marker_uuid=None):
        """計測を取得します。

        Args:
            uuid (str): 取得対象の計測のUUID
            marker_uuid (str): 計測マーカーのUUID（指定された計測マーカーに紐づく計測が取得されます）

        Returns:
            Measurement: 計測オブジェクト

        .. note::
            ``uuid`` と ``marker_uuid`` をいずれも指定しない場合、 ``Value Error`` が発生します。
            また、両方を指定した場合は計測のUUIDのみが使用されます。
        """
        if not uuid and not marker_uuid:
            raise ValueError("not selected measurement_uuid or marker_uuid")

        if uuid:
            path = "/api/v1/measurements/{uuid}".format(uuid=uuid)
            version = None
        else:
            path = "/api/v1/measurements/markers/{marker_uuid}/measurement".format(
                marker_uuid=marker_uuid
            )
            version = self.version["get_by_marker"]["version"]

        resp = json.loads(
            self.client._request(method="get", spath=path, version=version).text
        )

        return intdash.Measurement._from_dict(resp)

    def protect(self, uuid):
        """計測を保護します。

        Args:
            uuid (str): 保護対象の計測のUUID

        """
        self.client._request(
            method="put", spath="/api/v1/measurements/{uuid}/protect".format(uuid=uuid)
        )

    def unprotect(self, uuid):
        """計測の保護を解除します。

        Args:
            uuid (str): 保護解除対象の計測のUUID

        """
        self.client._request(
            method="put",
            spath="/api/v1/measurements/{uuid}/unprotect".format(uuid=uuid),
        )

    def update(self, uuid, name=None, description=None, basetime_type=None, ended=None):
        """計測を更新します。

        Args:
            uuid (str): 更新対象の計測のUUID
            name (str): 計測名
            description (str): 説明
            basetime_type (BasetimeType): 基準時刻タイプ
            ended (bool): 終了フラグ
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if basetime_type is not None:
            data["basetime_type"] = str(basetime_type)
        if ended is not None:
            data["ended"] = ended

        self.client._request(
            method="put",
            spath="/api/v1/measurements/{uuid}".format(uuid=uuid),
            json=data,
            code=requests.codes.no_content,
        )

    def delete(self, uuid):
        """計測をサーバーから削除します。

        Args:
            uuid (str): 削除対象の計測のUUID
        """
        self.client._request(
            method="delete",
            spath="/api/v1/measurements/{uuid}".format(uuid=uuid),
            code=requests.codes.no_content,
        )

    def _list(
        self,
        start,
        end,
        sort,
        order,
        limit,
        page,
        name,
        edge_uuid,
        partial_match,
        ended,
    ):
        query = {
            "sort": sort,
            "order": order,
            "limit": limit,
            "page": page,
            "partial_match": "true" if partial_match else "false",
        }

        # optional queries
        if name is not None:
            query["name"] = name
        if start is not None:
            query["start"] = timeutils.timestamp2unixmicro(start)
        if end is not None:
            query["end"] = timeutils.timestamp2unixmicro(end)
        if edge_uuid is not None:
            query["edge_uuid"] = edge_uuid
        if ended is not None:
            query["ended"] = "true" if ended else "false"

        return json.loads(
            self.client._request(
                method="get", spath="/api/v1/measurements", query=query
            ).text
        )

    def list(
        self,
        start=None,
        end=None,
        edge_uuid=None,
        name=None,
        partial_match=False,
        ended=None,
        sort="name",
        order="asc",
        limit=100,
        page=1,
        iterator=False,
    ):
        """計測のリストを取得します。

        Args:
            start (pandas.Timestamp): 取得対象範囲の始点
            end (pandas.Timestamp): 取得対象範囲の終点
            edge_uuid (str): 計測が紐づくエッジの UUID
            name (str): 計測名
            partial_match (bool): 部分一致フラグ
            ended (boolean): 終了フラグ
            sort (str): ソートに使用するフィールド名
            order (str): ソート順 ( ``asc`` or ``desc`` )
            limit (int): 最大取得件数
            page (int): ページ番号
            iterator (bool): Trueの場合、イテレータを生成します

        Returns:
            list[Measurement]: 計測オブジェクトのリスト


        .. note::
            ``partial_match`` では、計測の取得条件を指定できます。 ``False`` を指定すると、計測のbasetimeが取得対象範囲に入っている場合に、その計測が取得対象となります。
            ``True`` にすると、計測の一部が取得対象範囲に入っていればその計測は取得対象となります。

                .. parsed-literal::
                            | measurement1 |
                            +--------------+
                                                | measurement2 |
                                                +--------------+
                                    | measurement3 |
                                    +--------------+
                                                                        time
                    -----------+----------------------------+------------>
                               |                            |
                             start                         end

            上記の例では、``partial_match`` が ``True`` の場合、 `measurement1` 、 `measurement2` 、 `measurement3` が取得できます。
            ``partial_match`` が ``False`` の場合、 `measurement2` 、 `measurement3` が取得できます。
        """

        if iterator:
            return self._iter_lists(
                start=start,
                end=end,
                sort=sort,
                order=order,
                limit=limit,
                page=page,
                edge_uuid=edge_uuid,
                ended=ended,
                name=name,
                partial_match=partial_match,
            )

        resp = self._list(
            start=start,
            end=end,
            sort=sort,
            order=order,
            limit=limit,
            page=page,
            edge_uuid=edge_uuid,
            ended=ended,
            name=name,
            partial_match=partial_match,
        )

        return [intdash.Measurement._from_dict(item) for item in resp["items"]]

    def _iter_lists(
        self,
        start,
        end,
        edge_uuid,
        name,
        partial_match,
        ended,
        sort,
        order,
        page,
        limit,
    ):
        resp = self._list(
            start=start,
            end=end,
            sort=sort,
            order=order,
            limit=limit,
            page=page,
            name=name,
            edge_uuid=edge_uuid,
            ended=ended,
            partial_match=partial_match,
        )

        page = resp["page"]
        first = page["first"]
        last = page["last"]
        next = page["next"]
        previous = page["previous"]

        yield [intdash.Measurement._from_dict(item) for item in resp["items"]]

        while True:
            if last:
                return

            resp = json.loads(self.client._request(method="get", spath=next).text)
            page = resp["page"]
            first = page["first"]
            last = page["last"]
            next = page["next"]
            previous = page["previous"]

            yield [intdash.Measurement._from_dict(item) for item in resp["items"]]
