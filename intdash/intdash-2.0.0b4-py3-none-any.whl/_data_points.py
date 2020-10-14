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
from intdash import protocol, timeutils

__all__ = ["DataPoints"]


class DataPoints(object):
    """時系列データ（データポイントリソース）へのアクセスオブジェクトです。"""

    def __init__(self):
        self.client = None

    def store(self, measurement_uuid, data_points, serial_number=0, final=True):
        """時系列データ（データポイント）をサーバーへ保存します。

        Args:
            measurement_uuid (str): 保存先の計測のUUID
            data_points (list[DataPoint]): 保存するデータポイントオブジェクトのリスト
            serial_number (int): セクションの通し番号
            final (bool): 最終フラグ

        Examples:
            `DataPoint` の `data_payload` には、バイナリデータを指定します。バイナリデータは、使用する `data_type` に合わせて `intdash.data.Data` の `to_payload()` を使用することにより作成できます。

            >>> data_points = [
                    DataPoint(
                        elapsed_time=pd.Timedelta(seconds=0) ,
                        data_type=DataType.int.value,
                        channel=1,
                        data_payload=intdash.data.Int(data_id='test', value=2).to_payload()
                    )
                ]

            >>> client.data_points.store(
                    measurement_uuid=sample_measurement.uuid,
                    data_points=data_points
                )
        """

        req = intdash._utils._create_req_store_protobuf(
            data_points=data_points,
            serial_number=0,
            measurement_uuid=measurement_uuid,
            final=final,
        )

        resp = self.client._request(
            method="post",
            spath="/api/v1/measurements/data",
            headers={"Content-Type": "application/protobuf"},
            data=req,
        ).content

        for ack in intdash._utils._read_resp_body(resp):
            if type(ack) != protocol.SectionAck:
                raise RuntimeError("unexpected datapoint received")

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
        """時系列データ（データポイント）のリストを取得します。

        Args:
            start (pandas.Timestamp): 取得対象範囲の始点
            end (pandas.Timestamp): 取得対象範囲の終点
            measurement_uuid (str): 取得元の計測のUUID
            edge_uuid (str): 取得元のエッジUUID
            edge_name (str): 取得元のエッジ名
            id_queries (list[IdQuery]): 取得対象のidのリスト
            labels (list[str]): 取得対象のラベル名
            limit (int): 最大取得件数
            iterator (bool): Trueの場合、イテレータを生成します
            exit_on_error (bool): Trueの場合、取得中にエラーが発生すると処理を中断し、中断前までのDataResponseのリストを返します

        Returns:
            list[DataResponse]: データオブジェクト

        Examples:
            出力されたintdash.DataResponseの `data_payload` はバイナリデータです。使用する `data_type` に合わせて、 `intdash.data.Data` の `from_payload()` を使用することで、物理値を得ることができます。

                >>> dps = client.data_points.list(
                        measurement_uuid=sample_measurement.uuid,
                        id_queries=[
                            intdash.IdQuery(
                                data_type=intdash.DataType.int.value,
                                data_id='test'
                            )
                        ],
                        start=timeutils.str2timestamp("2020-01-01T00:00:00.000000Z"),
                        end=timeutils.str2timestamp("2020-01-02T00:00:00.000000Z"),
                    )

                >>> print(intdash.data.Int.from_payload(dps[0].data_payload))
                data_type: int
                data_id: test
                value: 2

        .. note::
            ``measurement_uuid`` ``edge_uuid`` ``edge_name`` はいずれか1つを指定してください。
            同時に指定された場合、``measurement_uuid`` > ``edge_uuid`` > ``edge_name`` の優先順位で参照し、低順位のものは無視されます。

        .. note::
            ``labels`` と ``id_queries`` 両方を指定した場合、双方いずれかにあてはまるデータすべてが対象となります。
            (ただし ``labels`` については、別途「信号定義」を登録する必要があります)

        .. note::
            サーバー側の取得処理にて例外が発生すると、例外メッセージを格納したDataResponseが出力され、処理自体は正常に終了します (以下サンプル参照)。この時、Unitの ``data_type`` はStringです。
            例外発生時に処理を中断したい場合、 ``exit_on_error`` に ``True`` を指定してください。

        Examples:
            以下は、データ取得時に例外が発生した場合のサンプルです。
            エラーメッセージがDataResponseに格納されています。エラーメッセージを格納したDataResponseの `data_type` はStringです。 `data_id` には、エラーが発生したエンドポイントのnamespaceが出力されます。
            DataResponseの内容を確認することで、再取得や原因究明に使用できます。

            >>> dps = lc.data_points.list(
                        measurement_uuid=sample_measurement.uuid,
                        labels=['nmea'],
                        start=sample_measurement.basetime,
                        end=sample_measurement.basetime + pd.Timedelta(seconds=10)
                    )

            >>> import json
            >>> for p in dps:
                    if 'error' in p.data_id:
                        print(p)
                        data = intdash.data.String.from_payload(p.data_payload)
                        error_message = json.loads(data.value)['error_description']
                        raise ValueError(f'contains failed data: {error_message}')
            # time: 2020-06-23T05:08:25.676942000Z
            # measurement_uuid: 3b5b9bed-d509-4198-aea0-54ee714f7a5b
            # data_type: 10
            # channel: 1
            # data_id: intdash/measurement/get/data/error
            # data_payload: b'\x05error{"error":"converted_error","error_description":"Error occurred in signal conversion","error_extra":{"signal_channel":1,"signal_data_id":"GPRMC","signal_data_type":2,"signal_label":"nmea"}}'
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

        data_points = intdash._utils._read_resp_body_protobuf(resp)

        data = []
        for d in data_points:
            data.append(
                intdash.DataResponse(
                    time=timeutils.timestamp2str(
                        timeutils.unix2timestamp(d.time.seconds, d.time.nanos)
                    ),
                    measurement_uuid=d.measurement_uuid,
                    data_type=d.data_type,
                    data_id=d.data_id.split("/")[1],
                    channel=int(d.data_id.split("/")[0]),
                    data_payload=d.data_payload,
                )
            )

        return data

    def _getdatapoints_iterator(
        self, name, start, end, labels, id_queries, exit_on_error, limit=1000
    ):
        ended = False

        while True:
            if ended:
                return

            data_points = self._getdatapoints(
                name=name,
                start=start,
                end=end,
                labels=labels,
                id_queries=id_queries,
                limit=limit,
                exit_on_error=exit_on_error,
            )

            if len(data_points) == 0:
                return

            start = timeutils.str2timestamp(
                data_points[-1].time
            ) + timeutils.micro2timedelta(1)
            if end <= start:
                ended = True

            yield data_points
