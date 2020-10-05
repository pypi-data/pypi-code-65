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

from debtcollector import removals

import intdash

__all__ = ["Edges"]


class Edges(object):
    """エッジリソースへのアクセスオブジェクトです。"""

    def __init__(self):
        self.client = None

    def _list(self, name, nickname, type, email, disabled, sort, order, limit, page):
        # required of default queries
        query = {
            "sort": sort,
            "order": order,
            "limit": limit,
            "page": page,
            "disabled": disabled,
        }

        # optional queries
        if name is not None:
            query["name"] = name

        if nickname is not None:
            query["nickname"] = nickname

        if type is not None:
            query["type"] = type

        if email is not None:
            query["email"] = email

        return json.loads(
            self.client._request(method="get", spath="/api/v1/edges", query=query).text
        )

    def me(self):
        """intdashにアクセスしているエッジ自身を取得します。

        Returns:
            Edge: intdashにアクセスしているエッジ自身のオブジェクト
        """
        resp = json.loads(
            self.client._request(method="get", spath="/api/v1/edges/me").text
        )

        return intdash.Edge._from_dict(resp)

    def list(
        self,
        name=None,
        nickname=None,
        type=None,
        email=None,
        disabled=False,
        sort="name",
        order="asc",
        limit=100,
        page=1,
        iterator=False,
    ):
        """エッジのリストを取得します。

        Args:
            name (str): エッジ名
            nickname (str): 表示名
            type (EdgeType): エッジタイプ
            email (str): メールアドレス
            disabled (str): 有効フラグ
            sort (str): ソートに使用するフィールド
            order (str): ソート順 ( ``asc`` or ``desc`` )
            limit (int): 最大取得件数
            page (int): ページ番号
            iterator (bool): Trueの場合、イテレータを生成します

        Returns:
            list[Edge]: エッジオブジェクトのリスト
        """

        if iterator:
            return self._iter_lists(
                name=name,
                nickname=nickname,
                type=type,
                email=email,
                disabled=disabled,
                sort=sort,
                order=order,
                limit=limit,
                page=page,
            )

        resp = self._list(
            name=name,
            nickname=nickname,
            type=type,
            email=email,
            disabled=disabled,
            sort=sort,
            order=order,
            limit=limit,
            page=page,
        )

        return [intdash.Edge._from_dict(item) for item in resp["items"]]

    def _iter_lists(
        self, name, nickname, type, email, disabled, sort, order, page, limit
    ):
        resp = self._list(
            name=name,
            nickname=nickname,
            type=type,
            email=email,
            disabled=disabled,
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

        yield [intdash.Edge._from_dict(item) for item in resp["items"]]

        while True:
            if last:
                return

            resp = json.loads(self.client._request(method="get", spath=next).text)
            page = resp["page"]
            first = page["first"]
            last = page["last"]
            next = page["next"]
            previous = page["previous"]

            yield [intdash.Edge._from_dict(item) for item in resp["items"]]
