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
import abc
import io

import pandas as pd

from intdash import data
from intdash._internal import Comparable

from . import filter
from .parser import data as pdata
from .parser import element, field
from .parser import filter as pfilter

__all__ = [
    "Element",
    "StreamElement",
    "RequestElement",
    "UpstreamSpecRequest",
    "UpstreamSpecResponse",
    "DownstreamSpecRequest",
    "DownstreamSpecResponse",
    "DownstreamFilterRequest",
    "DownstreamFilterResponse",
    "MeasurementIDRequest",
    "MeasurementIDResponse",
    "SOSMarker",
    "EOSMarker",
    "SectionAck",
    "Unit",
    "UpstreamSpec",
    "DownstreamSpec",
    "DownstreamFilter",
    "DownstreamDataFilter",
]


class Element(Comparable, metaclass=abc.ABCMeta):
    """エレメントのベースクラスです。"""

    @staticmethod
    @abc.abstractmethod
    def _from(elem):
        pass

    @abc.abstractmethod
    def _to(self):
        pass


class StreamElement(Element):
    """ストリームIDをもつエレメントのベースクラスです。"""


class RequestElement(Element):
    """リクエストIDをもつエレメントのベースクラスです。"""


class UpstreamSpecRequest(RequestElement):
    """アップストリームスペック要求

    Attributes:
        req_id (int): リクエストID
        specs (list[UpstreamSpec]): アップストリームスペックのリスト
    """

    def __init__(self, req_id, specs):
        self.req_id = req_id
        self.specs = specs

    @staticmethod
    def _from(elem):
        return UpstreamSpecRequest(
            req_id=elem.req_id.value, specs=[UpstreamSpec._from(x) for x in elem.specs]
        )

    def _to(self):
        return element.UpstreamSpecRequest(
            req_id=field.Uint8(value=self.req_id),
            stream_num=field.Uint8(value=len(self.specs)),
            specs=[x._to() for x in self.specs],
        )


class UpstreamSpec(Comparable):
    """アップストリームスペック

    Attributes:
        stream_id (int): ストリームID
        store (bool): 永続化フラグ
        resend (bool): 再送フラグ
        measurement_uuid (str): 計測UUID
        src_edge_uuid (str): 送信元エッジUUID
        dst_edge_uuids (list[str]): 送信先エッジUUIDのリスト
    """

    def __init__(
        self, stream_id, store, resend, measurement_uuid, src_edge_uuid, dst_edge_uuids
    ):
        self.stream_id = stream_id
        self.store = store
        self.resend = resend
        self.measurement_uuid = measurement_uuid
        self.src_edge_uuid = src_edge_uuid
        self.dst_edge_uuids = dst_edge_uuids

    @staticmethod
    def _from(spec):
        return UpstreamSpec(
            stream_id=spec.stream_id.value,
            store=spec.store,
            resend=spec.resend,
            measurement_uuid=spec.measurement_uuid.value,
            src_edge_uuid=spec.src_edge_uuid.value,
            dst_edge_uuids=[x.value for x in spec.dst_edge_uuids],
        )

    def _to(self):
        elem = element.UpstreamSpec(
            stream_id=field.Uint8(value=self.stream_id),
            flags=field.Uint8(value=0),
            dst_num=field.Uint8(value=len(self.dst_edge_uuids)),
            measurement_uuid=field.Uuid(value=self.measurement_uuid),
            src_edge_uuid=field.Uuid(value=self.src_edge_uuid),
            dst_edge_uuids=[field.Uuid(value=x) for x in self.dst_edge_uuids],
        )
        elem.store = self.store
        elem.resend = self.resend
        return elem


class UpstreamSpecResponse(RequestElement):
    """アップストリームスペック応答

    Attributes:
        req_id (int): リクエストID
        result_code (int): 結果コード
    """

    def __init__(self, req_id, result_code):
        self.req_id = req_id
        self.result_code = result_code

    @staticmethod
    def _from(elem):
        return UpstreamSpecResponse(
            req_id=elem.req_id.value, result_code=elem.result_code.value
        )

    def _to(self):
        return element.UpstreamSpecResponse(
            req_id=field.Uint8(value=self.req_id),
            result_code=field.Uint8(value=self.result_code),
        )


class DownstreamSpecRequest(RequestElement):
    """ダウンストリームスペック要求

    Attributes:
        req_id (int): リクエストID
        specs (list[UpstreamSpec]): ダウンストリームスペックのリスト
    """

    def __init__(self, req_id, specs):
        self.req_id = req_id
        self.specs = specs

    @staticmethod
    def _from(elem):
        return DownstreamSpecRequest(
            req_id=elem.req_id.value,
            specs=[DownstreamSpec._from(x) for x in elem.specs],
        )

    def _to(self):
        return element.DownstreamSpecRequest(
            req_id=field.Uint8(value=self.req_id),
            stream_num=field.Uint8(value=len(self.specs)),
            specs=[x._to() for x in self.specs],
        )


class DownstreamSpec(Comparable):
    """ダウンストリームスペック

    Attributes:
        stream_id (int): ストリームID
        src_edge_uuid (str): 送信元エッジUUID
        dst_edge_uuid (str): 送信先エッジUUID
    """

    def __init__(self, stream_id, src_edge_uuid, dst_edge_uuid):
        self.stream_id = stream_id
        self.src_edge_uuid = src_edge_uuid
        self.dst_edge_uuid = dst_edge_uuid

    @staticmethod
    def _from(spec):
        return DownstreamSpec(
            stream_id=spec.stream_id.value,
            src_edge_uuid=spec.src_edge_uuid.value,
            dst_edge_uuid=spec.dst_edge_uuid.value,
        )

    def _to(self):
        return element.DownstreamSpec(
            stream_id=field.Uint8(value=self.stream_id),
            src_edge_uuid=field.Uuid(value=self.src_edge_uuid),
            dst_edge_uuid=field.Uuid(value=self.dst_edge_uuid),
        )


class DownstreamSpecResponse(RequestElement):
    """ダウンストリームスペック応答

    Attributes:
        req_id (int): リクエストID
        result_code (int): 結果コード
    """

    def __init__(self, req_id, result_code):
        self.req_id = req_id
        self.result_code = result_code

    @staticmethod
    def _from(elem):
        return DownstreamSpecResponse(
            req_id=elem.req_id.value, result_code=elem.result_code.value
        )

    def _to(self):
        return element.DownstreamSpecResponse(
            req_id=field.Uint8(value=self.req_id),
            result_code=field.Uint8(value=self.result_code),
        )


class DownstreamFilterRequest(RequestElement):
    """ダウンストリームフィルタ要求

    Attributes:
        req_id (int): リクエストID
        filters (list[DownstreamFilter]): ダウンストリームフィルタのリスト
    """

    def __init__(self, req_id, filters):
        self.req_id = req_id
        self.filters = filters

    @staticmethod
    def _from(elem):
        return DownstreamFilterRequest(
            req_id=elem.req_id.value,
            filters=[DownstreamFilter._from(x) for x in elem.filters],
        )

    def _to(self):
        return element.DownstreamFilterRequest(
            req_id=field.Uint8(value=self.req_id),
            stream_num=field.Uint8(value=len(self.filters)),
            filters=[x._to() for x in self.filters],
        )


class DownstreamFilter(Comparable):
    """ダウンストリームフィルタ

    Attributes:
        stream_id (int): ストリームID
        downstream_data_filters (list[DownstreamDataFilter]): ダウンストリームデータフィルタのリスト
    """

    def __init__(self, stream_id, downstream_data_filters):
        self.stream_id = stream_id
        self.downstream_data_filters = downstream_data_filters

    @staticmethod
    def _from(df):
        return DownstreamFilter(
            stream_id=df.stream_id.value,
            downstream_data_filters=[
                DownstreamDataFilter._from(x) for x in df.downstream_data_filters
            ],
        )

    def _to(self):
        return element.DownstreamFilter(
            stream_id=field.Uint8(value=self.stream_id),
            data_num=field.Uint16(value=len(self.downstream_data_filters)),
            downstream_data_filters=[x._to() for x in self.downstream_data_filters],
        )


class DownstreamDataFilter(Comparable):
    """ダウンストリームデータフィルタ

    Attributes:
        channel (int): チャンネル番号
        filter (filter.Filter): フィルタ
    """

    def __init__(self, channel, filter):
        self.channel = channel
        self.filter = filter

    @staticmethod
    def _from(ddf):
        bio = io.BytesIO(ddf.content.value)
        rd = io.BufferedReader(bio)
        pf = pfilter.type2filter(ddf.data_type.value)._read_from(rd)

        if ddf.data_type.value not in filter.filter2filter:
            raise NotImplementedError
        f = filter.filter2filter[ddf.data_type.value]._from(pf)

        return DownstreamDataFilter(channel=ddf.channel.value, filter=f)

    def _to(self):
        bio = io.BytesIO()

        if type(self.filter) == filter.Any:
            data_type = self.filter.data_type

        else:
            pf = self.filter._to()

            wr = io.BufferedWriter(bio)
            pf._write_to(wr)
            wr.flush()

            data_type = pfilter.filter2type(pf)

        content = bio.getvalue()

        return element.DownstreamDataFilter(
            channel=field.Uint8(value=self.channel),
            data_type=field.Uint8(value=data_type),
            length=field.Uint16(value=len(content)),
            content=field.Bytes(value=content),
        )


class DownstreamFilterResponse(RequestElement):
    """ダウンストリームフィルタ応答

    Attributes:
        req_id (int): リクエストID
        result_code (int): 結果コード
    """

    def __init__(self, req_id, result_code):
        self.req_id = req_id
        self.result_code = result_code

    @staticmethod
    def _from(elem):
        return DownstreamFilterResponse(
            req_id=elem.req_id.value, result_code=elem.result_code.value
        )

    def _to(self):
        return element.DownstreamFilterResponse(
            req_id=field.Uint8(value=self.req_id),
            result_code=field.Uint8(value=self.result_code),
        )


class MeasurementIDRequest(RequestElement):
    """計測ID要求

    Attributes:
        req_id (int): リクエストID
        edge_uuid (str): エッジUUID
    """

    def __init__(self, req_id, edge_uuid):
        self.req_id = req_id
        self.edge_uuid = edge_uuid

    @staticmethod
    def _from(elem):
        return MeasurementIDRequest(
            req_id=elem.req_id.value, edge_uuid=elem.edge_uuid.value
        )

    def _to(self):
        return element.MeasurementIdRequest(
            req_id=field.Uint8(value=self.req_id),
            edge_uuid=field.Uuid(value=self.edge_uuid),
        )


class MeasurementIDResponse(RequestElement):
    """計測ID応答

    Attributes:
        req_id (int): リクエストID
        result_code (int): 結果コード
        measurement_uuid (str): 計測UUID
    """

    def __init__(self, req_id, result_code, measurement_uuid):
        self.req_id = req_id
        self.result_code = result_code
        self.measurement_uuid = measurement_uuid

    @staticmethod
    def _from(elem):
        return MeasurementIDResponse(
            req_id=elem.req_id.value,
            result_code=elem.result_code.value,
            measurement_uuid=elem.measurement_uuid.value,
        )

    def _to(self):
        return element.MeasurementIdResponse(
            req_id=field.Uint8(value=self.req_id),
            result_code=field.Uint8(value=self.result_code),
            measurement_uuid=field.Uuid(value=self.measurement_uuid),
        )


class SOSMarker(StreamElement):
    """SOSマーカー

    Attributes:
        stream_id (int): ストリームID
        serial_number (int): 通し番号
    """

    def __init__(self, stream_id, serial_number):
        self.stream_id = stream_id
        self.serial_number = serial_number

    @staticmethod
    def _from(elem):
        return SOSMarker(
            stream_id=elem.stream_id.value, serial_number=elem.serial_number.value
        )

    def _to(self):
        return element.SosMarker(
            stream_id=field.Uint8(value=self.stream_id),
            serial_number=field.Uint32(value=self.serial_number),
        )


class EOSMarker(StreamElement):
    """SOSマーカー

    Attributes:
        stream_id (int): ストリームID
        final (bool): 最終フラグ
        serial_number (int): 通し番号
    """

    def __init__(self, stream_id, final, serial_number):
        self.stream_id = stream_id
        self.final = final
        self.serial_number = serial_number

    @staticmethod
    def _from(elem):
        return EOSMarker(
            stream_id=elem.stream_id.value,
            final=elem.final,
            serial_number=elem.serial_number.value,
        )

    def _to(self):
        elem = element.EosMarker(
            stream_id=field.Uint8(value=self.stream_id),
            flags=field.Uint8(value=0),
            serial_number=field.Uint32(value=self.serial_number),
        )
        elem.final = self.final
        return elem


class SectionAck(StreamElement):
    """SOSマーカー

    Attributes:
        stream_id (int): ストリームID
        result_code (int): 結果コード
        serial_number (int): 通し番号
    """

    def __init__(self, stream_id, result_code, serial_number):
        self.stream_id = stream_id
        self.result_code = result_code
        self.serial_number = serial_number

    @staticmethod
    def _from(elem):
        return SectionAck(
            stream_id=elem.stream_id.value,
            result_code=elem.result_code.value,
            serial_number=elem.serial_number.value,
        )

    def _to(self):
        return element.SectionAck(
            stream_id=field.Uint8(value=self.stream_id),
            result_code=field.Uint8(value=self.result_code),
            serial_number=field.Uint32(value=self.serial_number),
        )


class Unit(StreamElement):
    """ユニット

    Attributes:
        stream_id (int): ストリームID
        channel (int): チャンネル番号
        elapsed_time (pandas.Timedelta): 経過時間
        data (data.Data): データ
    """

    def __init__(self, stream_id, channel, elapsed_time, data):
        self.stream_id = stream_id
        self.channel = channel
        self.elapsed_time = elapsed_time
        self.data = data

    @staticmethod
    def _from(elem):
        if elem.elapsed_time_frac.len == 2:
            elapsed_time = pd.Timedelta(
                seconds=elem.elapsed_time_sec.value,
                milliseconds=elem.elapsed_time_frac.value,
            )
        if elem.elapsed_time_frac.len == 3:
            elapsed_time = pd.Timedelta(
                seconds=elem.elapsed_time_sec.value,
                microseconds=elem.elapsed_time_frac.value,
            )
        if elem.elapsed_time_frac.len == 4:
            elapsed_time = pd.Timedelta(
                seconds=elem.elapsed_time_sec.value,
                microseconds=elem.elapsed_time_frac.value * 1e-3,
            )

        bio = io.BytesIO(elem.content.value)
        rd = io.BufferedReader(bio)
        pdta = pdata.type2data(elem.data_type.value)._read_from(rd)

        if elem.data_type.value not in data.data2data:
            raise NotImplementedError
        d = data.data2data[elem.data_type.value]._from(pdta)

        return Unit(
            stream_id=elem.stream_id.value,
            channel=elem.channel.value,
            elapsed_time=elapsed_time,
            data=d,
        )

    def _to(self):
        pdta = self.data._to()

        bio = io.BytesIO()
        wr = io.BufferedWriter(bio)
        pdta._write_to(wr)
        wr.flush()

        data_type = pdata.data2type(pdta)
        content = bio.getvalue()

        return element.Unit(
            stream_id=field.Uint8(value=self.stream_id),
            channel=field.Uint8(value=self.channel),
            data_type=field.Uint8(value=data_type),
            elapsed_time_sec=field.VarUint16to24(
                value=self.elapsed_time.seconds, len=3
            ),  # NOTE fixed to uint24
            elapsed_time_frac=field.VarUint16to32(
                value=self.elapsed_time.microseconds, len=3
            ),  # NOTE fixed to uint24
            length=field.VarUint8to32(
                value=len(content), len=4
            ),  # NOTE fixed to uint32
            content=field.Bytes(value=content),
        )
