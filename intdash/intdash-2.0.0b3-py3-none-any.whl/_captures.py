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

__all__ = ["Captures"]


class Captures(object):
    """キャプチャリソースへのアクセスオブジェクトです。"""

    def __init__(self):
        self.client = None

    def create(self, name, start, duration=None, shared=True, description=""):
        """キャプチャをサーバーへ作成します。

        Args:
            name (str): キャプチャ名
            start (pandas.Timestamp): 開始時刻
            description (str): 説明
            shared (bool): 共有フラグ
            duration (pandas.Timedelta): 継続時間

        Returns:
            Capture: 作成されたキャプチャオブジェクト
        """
        data = {
            "name": name,
            "description": description,
            "start": timeutils.timestamp2str(start),
            "duration": timeutils.timedelta2micro(duration)
            if duration is not None
            else 0,
            "shared": shared,
        }

        resp = json.loads(
            self.client._request(
                method="post",
                spath="/api/v1/captures",
                json=data,
                code=requests.codes.created,
            ).text
        )

        return intdash.Capture._from_dict(resp)

    def get(self, uuid):
        """キャプチャを取得します。

        Args:
            uuid (str): 取得対象のキャプチャの UUID

        Returns:
            Capture: キャプチャブジェクト
        """

        resp = json.loads(
            self.client._request(
                method="get", spath="/api/v1/captures/{uuid}".format(uuid=uuid)
            ).text
        )

        return intdash.Capture._from_dict(resp)

    def update(
        self, uuid, name=None, start=None, duration=None, shared=None, description=None
    ):
        """キャプチャを更新します。

        Args:
            uuid (str): 更新対象の計測のUUID
            name (str): キャプチャ名
            start (pandas.Timestamp): 開始時刻
            duration (pandas.Timedelta): 継続時間
            shared (bool): 共有フラグ
            description (str): 説明
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if start is not None:
            data["start"] = timeutils.timestamp2str(start)
        if duration is not None:
            data["duration"] = timeutils.timedelta2micro(duration)
        if shared is not None:
            data["shared"] = shared

        self.client._request(
            method="put",
            spath="/api/v1/captures/{uuid}".format(uuid=uuid),
            json=data,
            code=requests.codes.no_content,
        )

    def delete(self, uuid):
        """キャプチャをサーバーから削除します。

        Args:
            uuid (str): 削除対象のキャプチャのUUID
        """
        self.client._request(
            method="delete",
            spath="/api/v1/captures/{uuid}".format(uuid=uuid),
            code=requests.codes.no_content,
        )

    def _list(self, start, end, name, limit, sort, order, page):
        query = {
            "start": timeutils.timestamp2unixmicro(start),
            "end": timeutils.timestamp2unixmicro(end),
            "sort": sort,
            "order": order,
            "limit": limit,
            "page": page,
        }

        if name is not None:
            query["name"] = name

        return json.loads(
            self.client._request(
                method="get", spath="/api/v1/captures", query=query
            ).text
        )

    def list(
        self,
        start,
        end,
        name=None,
        sort="name",
        order="asc",
        limit=100,
        page=1,
        iterator=False,
    ):
        """キャプチャのリストを取得します。

        Args:
            start (pandas.Timestamp): 取得対象期間の開始時刻
            end (pandas.Timestamp): 取得対象期間の終了時刻
            name (str): キャプチャ名に対するクエリ
            sort (str): ソートに使用するフィールド名
            order (str): ソート順 ( ``asc`` or ``desc`` )
            limit (int): 最大取得件数
            page (int): ページ番号
            iterator (bool): Trueの場合、イテレータを生成します

        Returns:
            list[Capture]: キャプチャオブジェクトのリスト
        """

        if iterator:
            return self._iter_lists(
                start=start,
                end=end,
                name=name,
                sort=sort,
                order=order,
                page=page,
                limit=limit,
            )

        resp = self._list(
            start=start,
            end=end,
            name=name,
            sort=sort,
            order=order,
            page=page,
            limit=limit,
        )

        return [intdash.Capture._from_dict(item) for item in resp["items"]]

    def _iter_lists(self, start, end, name, sort, order, page, limit):
        resp = self._list(
            start=start,
            end=end,
            name=name,
            sort=sort,
            order=order,
            limit=limit,
            page=page,
        )

        page = resp["page"]
        first = page["first"]
        last = page["last"]
        next = page["next"]
        previous = page["previous"]

        yield [intdash.Capture._from_dict(item) for item in resp["items"]]

        while True:
            if last:
                return

            resp = json.loads(self.client._request(method="get", spath=next).text)
            page = resp["page"]
            first = page["first"]
            last = page["last"]
            next = page["next"]
            previous = page["previous"]

            yield [intdash.Capture._from_dict(item) for item in resp["items"]]
