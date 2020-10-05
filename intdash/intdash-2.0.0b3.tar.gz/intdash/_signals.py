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

__all__ = ["Signals"]


class Signals(object):
    """信号定義リソースへのアクセスオブジェクトです。"""

    def __init__(self):
        self.client = None

    def create(
        self, label, data_type, data_id, channel, conversion, display, description=""
    ):
        """信号定義をサーバー内に作成します。

        Args:
            label (str): ラベル名
            data_type (DataType): データタイプ
            data_id (str): データID
            channel (int): チャンネル
            conversion (Conversion): 変換定義
            display (Display): 表示定義
            description (str): 説明
        """
        data = {
            "label": label,
            "description": description,
            "data_type": data_type,
            "data_id": data_id,
            "channel": channel,
            "conversion": conversion._to_dict(),
            "display": display.__dict__,
        }

        resp = json.loads(
            self.client._request(method="post", spath="/api/v1/signals", json=data).text
        )

        return intdash.Signal._from_dict(resp)

    def get(self, uuid):
        """信号定義を取得します。

        Args:
            uuid (str): 取得対象の信号定義のUUID

        Returns:
            Signal: 信号定義ブジェクト
        """
        resp = json.loads(
            self.client._request(
                method="get", spath="/api/v1/signals/{uuid}".format(uuid=uuid)
            ).text
        )

        return intdash.Signal._from_dict(resp)

    def update(
        self,
        uuid,
        label=None,
        description=None,
        data_type=None,
        data_id=None,
        channel=None,
        conversion=None,
        display=None,
    ):
        """信号定義を更新します。

        Args:
            uuid (str): 更新対象の信号定義のUUID
            label (str): ラベル名
            description (str): 説明
            data_type (DataType): データタイプ
            data_id (str): データID
            channel (int): チャンネル
            conversion (Conversion): 変換定義
            display (Display): 表示定義
        """
        data = {}
        if label is not None:
            data["label"] = label
        if description is not None:
            data["description"] = description
        if data_type is not None:
            data["data_type"] = data_type
        if data_id is not None:
            data["data_id"] = data_id
        if channel is not None:
            data["channel"] = channel
        if conversion is not None:
            data["conversion"] = conversion._to_dict()
        if display is not None:
            data["display"] = display.__dict__

        self.client._request(
            method="put",
            spath="/api/v1/signals/{uuid}".format(uuid=uuid),
            json=data,
            code=requests.codes.no_content,
        )

    def delete(self, uuid):
        """信号定義をサーバーから削除します。

        Args:
            uuid (str): 削除対象の信号定義のUUID
        """
        self.client._request(
            method="delete",
            spath="/api/v1/signals/{uuid}".format(uuid=uuid),
            code=requests.codes.no_content,
        )

    def _list(self, limit, label, sort, order, page):
        query = {"sort": sort, "order": order, "limit": limit, "page": page}

        # optional queries
        if label is not None:
            query["label"] = label

        return json.loads(
            self.client._request(
                method="get", spath="/api/v1/signals", query=query
            ).text
        )

    def list(
        self, label=None, sort="label", order="asc", limit=100, page=1, iterator=False
    ):
        """信号定義のリストを取得します。

        Args:
            label (str): ラベル名
            sort (str): ソートに使用するフィールド名
            order (str): ソート順 ( ``asc`` or ``desc`` )
            limit (int): 最大取得件数
            page (int): ページ番号
            iterator (bool): Trueの場合、イテレータを生成します

        Returns:
            list[Signal]: 信号定義オブジェクトのリスト
        """

        if iterator:
            return self._iter_lists(
                limit=limit, label=label, sort=sort, order=order, page=page
            )

        resp = self._list(limit=limit, label=label, sort=sort, order=order, page=page)

        return [intdash.Signal._from_dict(item) for item in resp["items"]]

    def _iter_lists(self, sort, order, page, limit, label):
        resp = self._list(sort=sort, order=order, limit=limit, label=label, page=page)

        page = resp["page"]
        first = page["first"]
        last = page["last"]
        next = page["next"]
        previous = page["previous"]

        yield [intdash.Signal._from_dict(item) for item in resp["items"]]

        while True:
            if last:
                return

            resp = json.loads(self.client._request(method="get", spath=next).text)
            page = resp["page"]
            first = page["first"]
            last = page["last"]
            next = page["next"]
            previous = page["previous"]

            yield [intdash.Signal._from_dict(item) for item in resp["items"]]
