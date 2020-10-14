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
from debtcollector import removals

import intdash
from intdash import _utils, data, protocol, timeutils

__all__ = ["Units"]


class Units(object):
    """時系列データ（ユニット形式）へのアクセスオブジェクトです。"""

    def __init__(self):
        self.client = None

    def store(self, measurement_uuid, units, serial_number=0, final=True):
        """時系列データ（ユニットオブジェクト）をサーバーへ保存します。

        Args:
            measurement_uuid (str): 保存先の計測のUUID
            units (list[Unit]): 保存するユニットオブジェクトのリスト
            serial_number (int): セクションの通し番号
            final (bool): 最終フラグ
        """

        req = _utils._write_req_body(
            elems=_utils._create_elems_storedata(
                units=units, serial_number=serial_number, final=final
            )
        )

        resp = self.client._request(
            method="post",
            spath="/api/v1/measurements/{measurement_uuid}/data".format(
                measurement_uuid=measurement_uuid
            ),
            data=req,
        ).content

        for ack in _utils._read_resp_body(resp):
            if type(ack) != protocol.SectionAck:
                raise RuntimeError("unexpected unit received")

            if ack.result_code != protocol.ResultCode.OK:
                raise RuntimeError(
                    "result_code is not ok: {result_code}".format(
                        result_code=ack.result_code
                    )
                )

    def list(
        self,
        start,
        end,
        measurement_uuid=None,
        edge_uuid=None,
        edge_name=None,
        id_queries=None,
        labels=None,
        limit=1000,
        iterator=False,
        exit_on_error=False,
    ):
        """時系列データ（ユニットオブジェクト）のリストを取得します。

        Args:
            start (pandas.Timestamp): 取得対象期間の開始時刻
            end (pandas.Timestamp): 取得対象期間の終了時刻
            measurement_uuid (str): 取得元の計測のUUID
            edge_uuid (str): 取得元のエッジのUUID
            edge_name (str): 取得元のエッジ名
            id_queries (list[IdQuery]): 取得対象のidのリスト
            labels (list[str]): 取得対象のラベル名
            limit (int): 最大取得件数
            iterator (bool): Trueの場合、イテレータを生成します
            exit_on_error (bool): Trueの場合、取得中にエラーが発生すると処理を中断し、中断前までのUnitのリストを返します

        Returns:
            list[Unit]: ユニットオブジェクトのリスト

        .. note::
            ``measurement_uuid`` ``edge_uuid`` ``edge_name`` はいずれか1つを指定してください。
            同時に指定された場合、``measurement_uuid`` > ``edge_uuid`` > ``edge_name`` の優先順位で参照し、低順位のものは無視されます。

        .. note::
            ``labels`` と ``id_queries`` 両方を指定した場合、双方いずれかにあてはまるデータすべてが対象となります。
            (``labels`` を使用する際は、別途「信号定義」を登録する必要があります。)

        .. note::
            サーバー側の取得処理にて例外が発生すると、例外メッセージを格納したUnitが出力され、処理自体は正常に終了します (以下サンプル参照)。この時、Unitの ``data_type`` はStringです。
            例外発生時に処理を中断したい場合、 ``exit_on_error`` に ``True`` を指定してください。

        Examples:
            以下は、データ取得時に例外が発生した場合のサンプルです。エラーメッセージがUnitに格納されています。エラーメッセージを格納したUnitの `data_type` はStringです。 `id` には、エラーが発生したエンドポイントのnamespaceが出力されます。
            Unitの内容を確認することで、再取得や原因究明に使用できます。

            >>> us = lc.units.list(
                    measurement_uuid=sample_measurement.uuid,
                    labels=['nmea', 'test'],
                    start=sample_measurement.basetime,
                    end=sample_measurement.basetime + pd.Timedelta(seconds=10),
                    exit_on_error=False
                )

            >>> import json
            >>> for u in us:
                    if u.data.data_type.value == DataType.basetime.value:
                        continue
                    if 'error' in u.data.id:
                        print(u)
                        error_message =  json.loads(u.data.value)['error_description']
                        raise ValueError(f'contains failed data: {error_message}')
            # elapsed_time: 0 days 00:00:00
            # channel: 1
            # measurement_uuid: 3b5b9bed-d509-4198-aea0-54ee714f7a5b
            # data_type: string
            # id: intdash/measurement/get/data/error
            # value: {"error":"converted_error","error_description":"Error occurred in signal conversion","error_extra":{"signal_channel":1,"signal_data_id":"GPRMC","signal_data_type":2,"signal_label":"nmea"}}
            ValueError: contains failed data: Error occurred in signal conversion
        """

        name = None

        if measurement_uuid:
            name = measurement_uuid
        elif edge_uuid:
            name = edge_uuid
        elif edge_name:
            name = edge_name

        if name is None:
            raise ValueError(
                "please define `measurement_uuid` , `edge_uuid` or `edge_name`"
            )

        if iterator:
            return self._iter_lists(
                name=name,
                start=start,
                end=end,
                id_queries=id_queries,
                labels=labels,
                limit=limit,
                exit_on_error=exit_on_error,
            )

        return self._getdatapoints(
            name=name,
            start=start,
            end=end,
            labels=labels,
            id_queries=id_queries,
            limit=limit,
            exit_on_error=exit_on_error,
        )

    def _iter_lists(self, name, start, end, id_queries, labels, limit, exit_on_error):
        return self._getdatapoints_iterator(
            name=name,
            start=start,
            end=end,
            labels=labels,
            id_queries=id_queries,
            limit=limit,
            exit_on_error=exit_on_error,
        )

    def _getdatapoints(
        self, name, start, end, id_queries, labels, exit_on_error, limit=1000
    ):

        query = [
            ("name", name),
            ("start", timeutils.timestamp2str(start)),
            ("end", timeutils.timestamp2str(end)),
            ("limit", limit),
            ("exit_on_error", exit_on_error),
        ]

        if labels:
            for label in labels:
                query.append(("label", label))

        if id_queries:
            query.append(
                (
                    "idq",
                    [
                        "{data_type}:{channel}/{data_id}".format(
                            data_type=item.data_type,
                            channel=item.channel,
                            data_id=item.data_id,
                        )
                        for item in id_queries
                    ],
                )
            )

        resp = self.client._request(
            method="get",
            spath="/api/v1/data",
            query=query,
            headers={"Accept": "application/protobuf"},
        ).content

        data_points = _utils._read_resp_body_protobuf(resp)

        units = []
        basetime = None
        for d in data_points:
            if basetime is None:
                basetime = timeutils.unix2timestamp(d.time.seconds, d.time.nanos)
                units.append(
                    intdash.Unit(
                        elapsed_time=timeutils.micro2timedelta(0),
                        channel=0,
                        data=data.Basetime(
                            type=intdash.BasetimeType.volatile.value, basetime=basetime
                        ),
                    )
                )

            units.append(
                intdash.Unit(
                    elapsed_time=timeutils.unix2timestamp(d.time.seconds, d.time.nanos)
                    - basetime,
                    channel=int(d.data_id.split("/")[0]),
                    data=data.data2data[int(d.data_type)].from_payload(d.data_payload),
                    measurement_uuid=d.measurement_uuid,
                )
            )

        return units

    def _getdatapoints_iterator(
        self, name, start, end, labels, id_queries, exit_on_error, limit=1000
    ):
        ended = False

        while True:
            if ended:
                return

            units = self._getdatapoints(
                name=name,
                start=start,
                end=end,
                labels=labels,
                id_queries=id_queries,
                limit=limit,
                exit_on_error=exit_on_error,
            )

            only_basetime = True
            for u in units:
                d = u.data
                if type(d) != data.Basetime:
                    only_basetime = False
                    break

            if only_basetime:
                return

            basetime = None
            for u in units:
                d = u.data
                if type(d) == data.Basetime:
                    basetime = d.basetime
                    break

            start = basetime + units[-1].elapsed_time + timeutils.micro2timedelta(1)
            if end <= start:
                ended = True

            yield units
