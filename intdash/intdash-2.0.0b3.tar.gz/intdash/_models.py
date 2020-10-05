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
import enum

from intdash import timeutils
from intdash._internal import Comparable

NULL_UUID = "00000000-0000-0000-0000-000000000000"


__all__ = [
    "Edge",
    "EdgeType",
    "MeasurementBasetime",
    "BasetimeType",
    "Measurement",
    "MeasurementMarker",
    "MeasurementMarkerType",
    "MeasurementMarkerDetail",
    "MeasurementMarkerDetailPoint",
    "MeasurementMarkerDetailRange",
    "Unit",
    "DataResponse",
    "DataPoint",
    "DataType",
    "IdQuery",
    "DataFilter",
    "UpstreamSpec",
    "DownstreamSpec",
    "Signal",
    "Conversion",
    "ConversionNone",
    "ConversionJSON",
    "ConversionCSV",
    "ConversionNumFixedPoint",
    "ConversionNumFloatingPoint",
    "ConversionSubBytes",
    "ConversionSubString",
    "ConversionType",
    "Display",
    "Capture",
]


class EdgeType(str, enum.Enum):
    """エッジタイプを表す定数です。"""

    user = "user"
    device = "device"


class Edge(Comparable):
    """エッジリソースを表すオブジェクトです。

    Attributes:
        uuid (str): UUID
        name (str): エッジ名
        description (str): 説明
        nickname (str): 表示名
        type (EdgeType): エッジタイプ
        disabled (bool): 無効フラグ
        created_at (pandas.Timestamp): 作成時刻
        updated_at (pandas.Timestamp): 更新時刻
        last_login_at (pandas.Timestamp): 最終ログイン時刻
    """

    def __init__(
        self,
        uuid,
        name,
        description,
        nickname,
        type,
        disabled,
        created_at,
        updated_at,
        last_login_at,
    ):
        self.uuid = uuid
        self.name = name
        self.description = description
        self.nickname = nickname
        self.type = type
        self.disabled = disabled
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_login_at = last_login_at

    @staticmethod
    def _from_dict(dict):
        return Edge(
            uuid=dict["uuid"],
            name=dict["name"],
            description=dict["description"],
            nickname=dict["nickname"],
            type=dict["type"],
            disabled=dict["disabled"],
            created_at=timeutils.str2timestamp(dict["created_at"]),
            updated_at=timeutils.str2timestamp(dict["updated_at"]),
            last_login_at=timeutils.str2timestamp(dict["last_login_at"]),
        )


class BasetimeType(enum.Enum):
    """基準時刻のタイプを表す定数です。"""

    edge_rtc = int.from_bytes(b"\x01", "little")
    ntp = int.from_bytes(b"\x02", "little")
    gps = int.from_bytes(b"\x03", "little")
    volatile = int.from_bytes(b"\xfd", "little")
    api_first_received = int.from_bytes(b"\xfe", "little")
    manual = int.from_bytes(b"\xff", "little")

    def __str__(self):
        return self.name


class Measurement(Comparable):
    """計測リソースを表すオブジェクトです。

    Attributes:
        uuid (str): UUID
        name (str): 計測名
        description (str): 説明
        edge_uuid (str): 計測が紐づくエッジのUUID
        duration (pandas.Timedelta): 継続時間
        basetime (pandas.Timestamp): 基準時刻
        basetime_type (BasetimeType): 基準時刻タイプ
        ended (bool): 終了フラグ
        processed_ratio (float): 処理済み比率
        protected (bool): 保護状態
        markers (MeasurementMarker): 計測マーカー
        created_at (pandas.Timestamp): 作成時刻
        updated_at (pandas.Timestamp): 更新時刻
    """

    def __init__(
        self,
        uuid,
        name,
        description,
        edge_uuid,
        duration,
        basetime,
        basetime_type,
        ended,
        processed_ratio,
        protected,
        created_at,
        updated_at,
        markers=None,
    ):
        self.uuid = uuid
        self.name = name
        self.description = description
        self.edge_uuid = edge_uuid
        self.duration = duration
        self.ended = ended
        self.basetime = basetime
        self.basetime_type = basetime_type
        self.processed_ratio = processed_ratio
        self.protected = protected
        self.markers = markers
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def _from_dict(dict):
        if "markers" in dict:
            markers = [
                MeasurementMarker._from_dict(marker) for marker in dict["markers"]
            ]
        else:
            markers = None

        return Measurement(
            uuid=dict["uuid"],
            name=dict["name"],
            description=dict["description"],
            ended=dict["ended"],
            edge_uuid=dict["edge_uuid"],
            duration=timeutils.micro2timedelta(dict["duration"]),
            basetime=timeutils.str2timestamp(dict["basetime"]),
            basetime_type=dict["basetime_type"],
            processed_ratio=dict["processed_ratio"],
            protected=dict["protected"],
            markers=markers,
            created_at=timeutils.str2timestamp(dict["created_at"]),
            updated_at=timeutils.str2timestamp(dict["updated_at"]),
        )


class MeasurementBasetime(Comparable):
    """基準時刻リソースを表すオブジェクトです。

    Attributes:
        type (BasetimeType): 基準時刻タイプ
        basetime (pandas.Timestamp): 基準時刻
        created_at (pandas.Timestamp): 作成時刻
        updated_at (pandas.Timestamp): 更新時刻
    """

    def __init__(self, type, basetime, created_at, updated_at):
        self.basetime = basetime
        self.type = type
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def _from_dict(dict):
        return MeasurementBasetime(
            type=dict["type"],
            basetime=timeutils.str2timestamp(dict["basetime"]),
            created_at=timeutils.str2timestamp(dict["created_at"]),
            updated_at=timeutils.str2timestamp(dict["updated_at"]),
        )


class MeasurementMarker(Comparable):
    """計測マーカーを表すオブジェクトです。

    Attributes:
        uuid (str): UUID
        name (str): 計測マーカー名
        description (str): 計測マーカーの説明
        type (MeasurementMarkerType): 計測マーカーのタイプ
        detail (MeasurementMarkerDetail): 計測マーカーの詳細
        tag (dict): 計測マーカーのタグ
        created_at (pandas.Timestamp): 作成時刻
        created_by (str): 作成者
        updated_at (pandas.Timestamp): 更新時刻
        updated_by (str) : 更新者
    """

    def __init__(
        self,
        uuid,
        name,
        description,
        type,
        detail,
        tag,
        created_at,
        created_by,
        updated_at,
        updated_by,
    ):

        self.uuid = uuid
        self.name = name
        self.description = description
        self.type = type
        self.detail = detail
        self.tag = tag
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by

    @staticmethod
    def _from_dict(dict):
        return MeasurementMarker(
            uuid=dict["uuid"],
            name=dict["name"],
            description=dict["description"],
            type=MeasurementMarkerType(dict["type"]),
            detail=MeasurementMarkerDetail._from_dict(dict["detail"], dict["type"]),
            tag=dict["tag"],
            created_at=dict["created_at"],
            created_by=dict["created_by"],
            updated_at=dict["updated_at"],
            updated_by=dict["updated_by"],
        )


class MeasurementMarkerDetail(Comparable):
    """計測マーカーの詳細リクエスト用ベースクラスです。"""

    def _to_dict(self):
        return {k: timeutils.timedelta2micro(v) for k, v in self.__dict__.items()}

    @staticmethod
    def _from_dict(dict, type):
        d_timedelta = {k: timeutils.micro2timedelta(v) for k, v in dict.items()}
        if type == MeasurementMarkerDetailPoint.type:
            return MeasurementMarkerDetailPoint(**d_timedelta)
        if type == MeasurementMarkerDetailRange.type:
            return MeasurementMarkerDetailRange(**d_timedelta)


class MeasurementMarkerType(str, enum.Enum):
    """計測マーカーのタイプを表す定数です。"""

    point = "point"
    range = "range"


class MeasurementMarkerDetailPoint(MeasurementMarkerDetail):
    """計測の単発マーカーの詳細リクエスト用のオブジェクトです。

    Attributes:
        occurred_elapsed_time (pandas.Timedelta): 計測の開始時刻から計測マーカー発生時刻までの経過時間
    """

    type = MeasurementMarkerType.point.value

    def __init__(self, occurred_elapsed_time):
        self.occurred_elapsed_time = occurred_elapsed_time


class MeasurementMarkerDetailRange(MeasurementMarkerDetail):
    """計測の範囲マーカーの詳細リクエスト用のオブジェクトです。

    Attributes:
        start_elapsed_time (pandas.Timedelta): 計測の開始時刻から計測マーカー開始時刻までの経過時間
        end_elapsed_time (pandas.Timedelta): 計測の開始時刻から計測マーカーの終了時刻までの経過時間
    """

    type = MeasurementMarkerType.range.value

    def __init__(self, start_elapsed_time, end_elapsed_time):
        self.start_elapsed_time = start_elapsed_time
        self.end_elapsed_time = end_elapsed_time


class DataType(int, enum.Enum):
    """データタイプを表す定数です。"""

    can = int.from_bytes(b"\x01", "little")
    can_bulk = int.from_bytes(b"\x07", "little")
    nmea = int.from_bytes(b"\x02", "little")
    general_sensor = int.from_bytes(b"\x03", "little")
    general_sensor_bulk = int.from_bytes(b"\x08", "little")
    jpeg = int.from_bytes(b"\x09", "little")
    controlpad = int.from_bytes(b"\x04", "little")
    mavlink = int.from_bytes(b"\x05", "little")
    generic = int.from_bytes(b"\x7f", "little")
    basetime = int.from_bytes(b"\x87", "little")
    string = int.from_bytes(b"\x0a", "little")
    float = int.from_bytes(b"\x0b", "little")
    int = int.from_bytes(b"\x0c", "little")
    bytes = int.from_bytes(b"\x0e", "little")
    h264 = int.from_bytes(b"\x0d", "little")
    aac = int.from_bytes(b"\x10", "little")
    pcm = int.from_bytes(b"\x0f", "little")


class IdQuery(Comparable):
    """データの条件定義を表すオブジェクトです。

    Attributes:
        data_type (DataType): データタイプ
        channel (int): チャンネル
        data_id (str): データID
    """

    def __init__(self, data_type="*", channel="*", data_id="*"):
        self.data_type = data_type
        self.channel = channel
        self.data_id = data_id


class Unit(Comparable):
    """Unitリソースを表すオブジェクトです。

    Attributes:
        elapsed_time (pandas.Timedelta): 経過時間
        channel (int): チャンネル番号
        data (data.Data): データ
    """

    def __init__(self, elapsed_time, channel, data, measurement_uuid=None):
        self.measurement_uuid = measurement_uuid
        self.elapsed_time = elapsed_time
        self.channel = channel
        self.data = data

    def __str__(self) -> str:
        return "elapsed_time: {elapsed_time}\nchannel: {channel}\nmeasurement_uuid: {measurement_uuid}\n{data}".format(
            elapsed_time=self.elapsed_time,
            channel=self.channel,
            measurement_uuid=self.measurement_uuid,
            data=self.data,
        )


class DataResponse(Comparable):
    """サーバーから取得されたデータポイントは、DataResponseとして表現されます。ペイロードは、data_payloadで得ることができます。

    Attributes:
        time (pandas.Timestamp): データの発生時刻
        measurement_uuid (str): 計測UUID
        data_type (DataType): データタイプ
        data_id (str): データID
        channel (int): チャンネル番号
        data_payload (bytes): データのペイロード
    """

    def __init__(
        self, time, measurement_uuid, data_type, data_id, channel, data_payload
    ):
        self.time = time
        self.measurement_uuid = measurement_uuid
        self.data_type = data_type
        self.data_id = data_id
        self.channel = channel
        self.data_payload = data_payload

    def __str__(self) -> str:
        return "time: {time}\nmeasurement_uuid: {measurement_uuid}\ndata_type: {data_type}\nchannel: {channel}\ndata_id: {data_id}\ndata_payload: {data_payload}".format(
            time=self.time,
            measurement_uuid=self.measurement_uuid,
            data_type=self.data_type,
            data_id=self.data_id,
            channel=self.channel,
            data_payload=self.data_payload,
        )


class DataPoint(Comparable):
    """DataPointリソースを表すオブジェクトです。データをサーバーに保存する際に使用します。

    Attributes:
        elapsed_time (pandas.Timedelta): データの経過時間
        channel (int): チャンネル番号
        data_type (DataType): データタイプ
        data_payload (bytes): データのペイロード
    """

    def __init__(self, elapsed_time, data_type, channel, data_payload):
        self.elapsed_time = elapsed_time
        self.data_type = data_type
        self.channel = channel
        self.data_payload = data_payload

    def __str__(self) -> str:
        return "elapsed_time: {elapsed_time}\nndata_type: {data_type}\ndata: {data_payload}".format(
            elapsed_time=self.elapsed_time,
            data_type=self.data_type,
            channel=self.channel,
            data_payload=self.data_payload,
        )


class DataFilter(Comparable):
    """データフィルタを表すオブジェクトです。

    Attributes:
        data_type (DataType): データタイプ
        channel (int): チャンネル番号
        data_id (str): データID
    """

    def __init__(self, data_type, channel, data_id=None):
        self.data_type = data_type
        self.channel = channel
        self.data_id = data_id


class DownstreamSpec(Comparable):
    """ダウンストリームスペックを表すオブジェクトです。

    Attributes:
        src_edge_uuid (str): 送信元エッジUUID
        filters (list[DataFilter]): データフィルタのリスト
        dst_edge_uuid (str): 送信先エッジUUID
    """

    def __init__(self, src_edge_uuid, filters, dst_edge_uuid=NULL_UUID):
        self.src_edge_uuid = src_edge_uuid
        self.dst_edge_uuid = dst_edge_uuid
        self.filters = filters


class UpstreamSpec(Comparable):
    """アップストリームスペックを表すオブジェクトです。

    Attributes:
        src_edge_uuid (str): 送信元エッジUUID
        dst_edge_uuids (list[str]): 送信先エッジUUIDのリスト
        resend (bool): 再送フラグ
        store (bool): 永続化フラグ
        measurement_uuid (str): 計測UUID
    """

    def __init__(
        self,
        src_edge_uuid,
        dst_edge_uuids=None,
        resend=False,
        store=False,
        measurement_uuid=NULL_UUID,
    ):
        self.src_edge_uuid = src_edge_uuid
        self.dst_edge_uuids = dst_edge_uuids if dst_edge_uuids is not None else []
        self.resend = resend
        self.store = store
        self.measurement_uuid = measurement_uuid


class Signal(Comparable):
    """信号定義リソースを表すオブジェクトです。

    Attributes:
        uuid (str): UUID
        label (str): ラベル名
        description (str): 説明
        data_type (DataType): データタイプ
        data_id (str): データID
        channel (int): チャンネル番号
        conversion (Conversion): 変換定義
        display (Display): 表示定義
        hash (str): 信号定義のハッシュ
        created_at (pandas.Timestamp): 作成時刻
        updated_at (pandas.Timestamp): 更新時刻
    """

    def __init__(
        self,
        uuid,
        label,
        description,
        data_type,
        data_id,
        channel,
        conversion,
        display,
        hash,
        created_at,
        updated_at,
    ):
        self.uuid = uuid
        self.label = label
        self.description = description
        self.data_type = data_type
        self.data_id = data_id
        self.channel = channel
        self.conversion = conversion
        self.display = display
        self.hash = hash
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def _from_dict(dict):
        return Signal(
            uuid=dict["uuid"],
            label=dict["label"],
            description=dict["description"],
            data_type=dict["data_type"],
            data_id=dict["data_id"],
            channel=dict["channel"],
            conversion=Conversion._from_dict(dict["conversion"]),
            display=Display(**dict["display"]),
            hash=dict["hash"],
            created_at=timeutils.str2timestamp(dict["created_at"]),
            updated_at=timeutils.str2timestamp(dict["updated_at"]),
        )


class Conversion(Comparable):
    """変換定義のベースクラスです。

    Attributes:
        type (ConversionType): 変換定義のタイプ
        options (dict): 変換定義の詳細
    """

    @staticmethod
    def _from_dict(d):
        type = d["type"]
        if type == ConversionNone.type:
            return ConversionNone(**d["options"])
        if type == ConversionJSON.type:
            return ConversionJSON(**d["options"])
        if type == ConversionCSV.type:
            return ConversionCSV(**d["options"])
        if type == ConversionNumFloatingPoint.type:
            return ConversionNumFloatingPoint(**d["options"])
        if type == ConversionNumFixedPoint.type:
            return ConversionNumFixedPoint(**d["options"])
        if type == ConversionSubBytes.type:
            return ConversionSubBytes(**d["options"])
        if type == ConversionSubString.type:
            return ConversionSubString(**d["options"])

    def _to_dict(self):
        return {
            "type": self.type,
            "options": {k: v for k, v in self.__dict__.items() if k != "type"},
        }


class ConversionType(str, enum.Enum):
    """変換タイプを表す定数です。"""

    none = "none"
    json = "json"
    csv = "csv"
    num_floating_point = "num_floating_point"
    num_fixed_point = "num_fixed_point"
    sub_bytes = "sub_bytes"
    sub_string = "sub_string"


class ConversionNone(Conversion):
    """変換を行わない場合に使用する変換定義です。"""

    type = ConversionType.none.value


class ConversionJSON(Conversion):
    """JSONからの変換を定義するオブジェクトです。

    Attributes:
        fieldpath (str): フィールドパス
        value_type (str): 出力値タイプ (``str`` or ``num``)
    """

    type = ConversionType.json.value

    def __init__(self, fieldpath, value_type):
        self.fieldpath = fieldpath
        self.value_type = value_type


class ConversionCSV(Conversion):
    """CSVからの変換を定義するオブジェクトです。

    Attributes:
        delimiters (list[str]): デリミタのリスト
        index (int): インデックス
        value_type (str): 出力値タイプ (``str`` or ``num``)
    """

    type = ConversionType.csv.value

    def __init__(self, delimiters, index, value_type):
        self.delimiters = delimiters
        self.index = index
        self.value_type = value_type


class ConversionNumFloatingPoint(Conversion):
    """浮動小数点数としての読み出しを表す変換定義オブジェクトです。

    Attributes:
        startbyte (int): 開始バイト位置
        endian (str): エンディアン (``little`` or ``big``)
        precision (int): 精度 (``64`` or ``32``)
    """

    type = ConversionType.num_floating_point.value

    def __init__(self, startbyte, endian, precision):
        self.startbyte = startbyte
        self.endian = endian
        self.precision = precision


class ConversionNumFixedPoint(Conversion):
    """固定小数点数としての読み出しを表す変換定義オブジェクトです。

    Attributes:
        startbit (int): 開始ビット位置
        bitsize (int): ビットサイズ
        endian (str): エンディアン (``little`` or ``big``)
        sign (str): 符号有無 (``signed`` or ``unsigned``)
        scale (float): スケールファクター
        offset (float): オフセット
    """

    type = ConversionType.num_fixed_point.value

    def __init__(self, startbit, bitsize, endian, sign, scale, offset):
        self.startbit = startbit
        self.bitsize = bitsize
        self.endian = endian
        self.sign = sign
        self.scale = scale
        self.offset = offset


class ConversionSubString(Conversion):
    """文字列の切り出しを表す変換定義オブジェクトです。

    Attributes:
        startbyte (int): 開始バイト位置
        bytesize (int): バイトサイズ
    """

    type = ConversionType.sub_string.value

    def __init__(self, startbyte, bytesize):
        self.startbyte = startbyte
        self.bytesize = bytesize


class ConversionSubBytes(Conversion):
    """バイト列の切り出しを表す変換定義オブジェクトです。

    Attributes:
        startbyte (int): 開始バイト位置
        bytesize (int): バイトサイズ
    """

    type = ConversionType.sub_bytes.value

    def __init__(self, startbyte, bytesize):
        self.startbyte = startbyte
        self.bytesize = bytesize


class Display(Comparable):
    """表示の定義を表すオブジェクトです。

    Attributes:
        unit (str): 単位
        min (float): 最小値
        max (float): 最大値
        format (str): フォーマット
    """

    def __init__(self, unit, min, max, format):
        self.unit = unit
        self.min = min
        self.max = max
        self.format = format


class Capture(Comparable):
    """キャプチャリソースを表すオブジェクトです。

    Attributes:
        uuid (str): UUID
        name (str): キャプチャ名
        description (str): 説明
        start (pandas.Timestamp): 開始時刻
        duration (pandas.Timedelta): 継続時間
        edge_uuid (str): キャプチャが紐づくエッジのUUID
        shared (bool): 共有フラグ
        created_at (pandas.Timestamp): 作成時刻
        updated_at (pandas.Timestamp): 更新時刻
    """

    def __init__(
        self,
        uuid,
        name,
        description,
        start,
        duration,
        edge_uuid,
        shared,
        created_at,
        updated_at,
    ):
        self.uuid = uuid
        self.name = name
        self.description = description
        self.start = start
        self.duration = duration
        self.edge_uuid = edge_uuid
        self.shared = shared
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def _from_dict(dict):
        return Capture(
            uuid=dict["uuid"],
            name=dict["name"],
            description=dict["description"],
            start=timeutils.str2timestamp(dict["start"]),
            duration=timeutils.micro2timedelta(dict["duration"]),
            edge_uuid=dict["edge_uuid"],
            shared=dict["shared"],
            created_at=timeutils.str2timestamp(dict["created_at"]),
            updated_at=timeutils.str2timestamp(dict["updated_at"]),
        )
