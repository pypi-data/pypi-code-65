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
import struct

from intdash import timeutils
from intdash._internal import Comparable
from intdash.protocol.parser import data, field

__all__ = [
    "Data",
    "RawData",
    "ValueData",
    "CAN",
    "NMEA",
    "GeneralSensor",
    "Controlpad",
    "Generic",
    "JPEG",
    "Float",
    "String",
    "Int",
    "Bytes",
    "Basetime",
    "H264",
    "AAC",
    "PCM",
    "data2data",
]

DISPLAY_MAX_LENGTH = 20


class Data(Comparable, metaclass=abc.ABCMeta):
    """intdash で定義されるデータ型のベースクラスです。"""

    @staticmethod
    @abc.abstractmethod
    def _from(elem):
        pass

    @abc.abstractmethod
    def _to(self):
        pass

    def to_payload(self):
        """データオブジェクトをデータのペイロードに変換します。"""

        bio = io.BytesIO()
        wr = io.BufferedWriter(bio)

        self._to()._write_to(wr)
        wr.flush()

        return bio.getvalue()


class RawData(Data):
    def __str__(self) -> str:
        data = ["%02X" % b for b in self.data]
        if len(data) < DISPLAY_MAX_LENGTH:
            s = " ".join(data)
        else:
            s = " ".join(data[:DISPLAY_MAX_LENGTH]) + " ..."

        return "data_type: {data_type}\ndata_id: {id}\ndata: {s}".format(
            data_type=self.data_type.name, id=self.data_id, s=s
        )


class ValueData(RawData):
    def __str__(self) -> str:
        return "data_type: {data_type}\ndata_id: {id}\nvalue: {value}".format(
            data_type=self.data_type.name, id=self.data_id, value=self.value
        )


class CAN(RawData):
    """CANのデータを表すオブジェクトです。

    Attributes:
        decimal_id (int): データIDの10進数表記
        data (bytes): 表現されるデータ
    """

    data_type = data.DataType.can
    """データタイプ
    """

    def __init__(self, decimal_id, data):
        self.decimal_id = decimal_id
        self.data = data

    @staticmethod
    def _from(data):
        return CAN(decimal_id=data.id.value, data=data.data.value)

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを Can オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """
        return CAN(
            decimal_id=int.from_bytes(data_payload[:4], byteorder="little"),
            data=data_payload[5:],
        )

    def _to(self):
        return data.CAN(
            id=field.Uint32(value=self.decimal_id),
            dlc=field.Uint8(value=len(self.data)),
            data=field.Bytes(value=self.data),
        )

    @property
    def data_id(self):
        """データID"""
        return "%08x" % self.decimal_id


class NMEA(RawData):
    """NMEAのデータを表すオブジェクトです。

    Attributes:
        string (str): 表現されるデータ

    .. note::
        `data_id` は NmeaString 内のトーカとメッセージ5文字を UTF-8 エンコード した値が指定されます。
    """

    data_type = data.DataType.nmea
    """データタイプ
    """

    def __init__(self, string):
        self.string = string

    @staticmethod
    def _from(data):
        return NMEA(string=data.string.value)

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを Nmea オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """
        return NMEA(string=data_payload.decode("utf-8"))

    def _to(self):
        return data.NMEA(string=field.String(value=self.string))

    @property
    def data_id(self):
        """データID"""
        return self.string[1:6]

    @property
    def data(self):
        return self.string.encode("utf-8")

    @property
    def value(self):
        return self.string


class GeneralSensor(RawData):
    """汎用センサのデータを表すオブジェクトです。

    Attributes:
        decimal_id (int): データIDの10進数表記
        data (bytes): 表現されるデータ
    """

    data_type = data.DataType.general_sensor
    """データタイプ
    """

    def __init__(self, decimal_id, data):
        self.decimal_id = decimal_id
        self.data = data

    @staticmethod
    def _from(data):
        return GeneralSensor(decimal_id=data.id.value, data=data.data.value)

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを GeneralSensor オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """

        return GeneralSensor(
            decimal_id=int.from_bytes(data_payload[:2], byteorder="little"),
            data=data_payload[2:],
        )

    def _to(self):
        return data.GeneralSensor(
            id=field.Uint16(value=self.decimal_id), data=field.Bytes(value=self.data)
        )

    @property
    def data_id(self):
        """データID"""
        return "%04x" % self.decimal_id


class JPEG(RawData):
    """JPEGのデータを表すオブジェクトです。

    Attributes:
        data (bytes): 表現されるデータ
    """

    data_type = data.DataType.jpeg
    """データタイプ
    """

    data_id = "jpeg"
    """データID
    """

    def __init__(self, data):
        self.data = data

    @staticmethod
    def _from(data):
        return JPEG(data=data.data.value)

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを JPEG オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """
        return JPEG(data=data_payload)

    def _to(self):
        return data.JPEG(data=field.Bytes(value=self.data))


class H264(RawData):
    """H.264のデータを表すオブジェクトです。

    Attributes:
        type_id (int): データ部の種別番号
        data (bytes): 表現されるデータ
    """

    data_type = data.DataType.h264
    """データタイプ
    """

    def __init__(self, type_id, data):
        self.type_id = type_id
        self.data = data

    @staticmethod
    def _from(data):
        return H264(type_id=data.type_id.value, data=data.data.value)

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを H264 オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """
        return H264(
            type_id=int.from_bytes(data_payload[:1], byteorder="little"),
            data=data_payload[1:],
        )

    def _to(self):
        return data.H264(
            type_id=field.Uint8(value=self.type_id), data=field.Bytes(value=self.data)
        )

    @property
    def data_id(self):
        """データID"""
        return "%02x" % self.type_id


class AAC(RawData):
    """AACのデータを表すオブジェクトです。

    Attributes:
        data (bytes): 表現されるデータ
    """

    data_type = data.DataType.aac
    """データタイプ
    """

    data_id = "aac"
    """データID
    """

    def __init__(self, data):
        self.data = data

    @staticmethod
    def _from(data):
        return AAC(data=data.data.value)

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを AAC オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """
        return AAC(data=data_payload)

    def _to(self):
        return data.AAC(data=field.Bytes(value=self.data))


class PCM(RawData):
    """PCMのデータを表すオブジェクトです。

    Attributes:
        format_id (int): フォーマットID
        channels (int): pcmチャンネル数
        sample_rate (int): サンプルレート
        bit_per_sample (int):  ビットレート
        data (bytes): 表現されるデータ
    """

    data_type = data.DataType.pcm
    """データタイプ
    """

    data_id = "pcm"
    """データID
    """

    def __init__(self, format_id, channels, sample_rate, bit_per_sample, data):
        self.format_id = format_id
        self.channels = channels
        self.sample_rate = sample_rate
        self.bit_per_sample = bit_per_sample
        self.data = data

    @staticmethod
    def _from(data):
        return PCM(
            format_id=data.format_id.value,
            channels=data.channels.value,
            sample_rate=data.sample_rate.value,
            bit_per_sample=data.bit_per_sample.value,
            data=data.data.value,
        )

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを PCM オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """
        return PCM(
            format_id=int.from_bytes(data_payload[:2], byteorder="little"),
            channels=int.from_bytes(data_payload[2:4], byteorder="little"),
            sample_rate=int.from_bytes(data_payload[4:8], byteorder="little"),
            bit_per_sample=int.from_bytes(data_payload[8:10], byteorder="little"),
            data=data_payload[10:],
        )

    def _to(self):
        return data.PCM(
            format_id=field.Uint16(value=self.format_id),
            channels=field.Uint16(value=self.channels),
            sample_rate=field.Uint32(value=self.sample_rate),
            bit_per_sample=field.Uint16(value=self.bit_per_sample),
            data=field.Bytes(value=self.data),
        )


class Controlpad(RawData):
    """コントロールパッドのデータを表すオブジェクトです。

    Attributes:
        decimal_id (int): データIDの10進数表記
        data (bytes): 表現されるデータ
    """

    data_type = data.DataType.controlpad
    """データタイプ
    """

    def __init__(self, decimal_id, data):
        self.decimal_id = decimal_id
        self.data = data

    @staticmethod
    def _from(data):
        return Controlpad(decimal_id=data.id.value, data=data.data.value)

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを Controlpad オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """
        return Controlpad(
            decimal_id=int.from_bytes(data_payload[:1], byteorder="little"),
            data=data_payload[1:],
        )

    def _to(self):
        return data.Controlpad(
            id=field.Uint8(value=self.decimal_id), data=field.Bytes(value=self.data)
        )

    @property
    def data_id(self):
        """データID"""
        return "%02x" % self.decimal_id


class Generic(RawData):
    """汎用データのデータを表すオブジェクトです。

    Attributes:
        decimal_id (int): データID
        data (bytes): 表現されるデータ
    """

    data_type = data.DataType.generic
    """データタイプ
    """

    def __init__(self, decimal_id, data):
        self.decimal_id = decimal_id
        self.data = data

    @staticmethod
    def _from(data):
        return Generic(decimal_id=data.id.value, data=data.data.value)

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを Generic オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """
        return Generic(
            decimal_id=int.from_bytes(data_payload[:4], byteorder="little"),
            data=data_payload[4:],
        )

    def _to(self):
        return data.Generic(
            id=field.Uint32(value=self.decimal_id), data=field.Bytes(value=self.data)
        )

    @property
    def data_id(self):
        """データID"""
        return "%08x" % self.decimal_id


class Float(ValueData):
    """倍精度浮動小数点数のデータを表すオブジェクトです。

    Attributes:
        data_id (str): データID
        value (float): 表現されるデータ
    """

    data_type = data.DataType.float
    """データタイプ
    """

    def __init__(self, data_id, value):
        self.data_id = data_id
        self.value = value

    @staticmethod
    def _from(data):
        return Float(data_id=data.id.value, value=data.value.value)

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを Float オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """
        id_length = int.from_bytes(data_payload[:1], byteorder="little")
        data_id = data_payload[1 : 1 + id_length].decode("utf-8")
        value = struct.unpack("<d", data_payload[1 + id_length :])[0]
        return Float(data_id=data_id, value=value)

    def _to(self):
        return data.Float(
            id_length=field.Uint8(value=len(self.data_id)),
            id=field.String(value=self.data_id),
            value=field.Float64(value=self.value),
        )

    @property
    def data(self):
        bs = struct.pack("<d", self.value)
        return bs


class String(ValueData):
    """文字列のデータを表すオブジェクトです。

    Attributes:
        data_id (str): データID
        value (str): 表現されるデータ
    """

    data_type = data.DataType.string
    """データタイプ
    """

    def __init__(self, data_id, value):
        self.data_id = data_id
        self.value = value

    @staticmethod
    def _from(data):
        return String(data_id=data.id.value, value=data.value.value)

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを String オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """
        id_length = int.from_bytes(data_payload[:1], byteorder="little")
        data_id = data_payload[1 : 1 + id_length].decode("utf-8")
        value = data_payload[1 + id_length :].decode("utf-8")
        return String(data_id=data_id, value=value)

    def _to(self):
        return data.String(
            id_length=field.Uint8(value=len(self.data_id)),
            id=field.String(value=self.data_id),
            value=field.String(value=self.value),
        )

    @property
    def data(self):
        return self.value.encode("utf-8")


class Int(ValueData):
    """64bit符号付き整数のデータを表すオブジェクトです。

    Attributes:
        data_id (str): データID
        value (int): 表現されるデータ
    """

    data_type = data.DataType.int
    """データタイプ
    """

    def __init__(self, data_id, value):
        self.data_id = data_id
        self.value = value

    @staticmethod
    def _from(data):
        return Int(data_id=data.id.value, value=data.value.value)

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを Int オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """
        id_length = int.from_bytes(data_payload[:1], byteorder="little")
        data_id = data_payload[1 : 1 + id_length].decode("utf-8")
        value = int.from_bytes(data_payload[1 + id_length :], byteorder="little")
        return Int(data_id=data_id, value=value)

    def _to(self):
        return data.Int(
            id_length=field.Uint8(value=len(self.data_id)),
            id=field.String(value=self.data_id),
            value=field.Int64(value=self.value),
        )

    @property
    def data(self):
        return self.value


class Bytes(ValueData):
    """バイト列のデータを表すオブジェクトです。

    Attributes:
        data_id (str): データID
        value (bytes): 表現されるデータ
    """

    data_type = data.DataType.bytes
    """データタイプ
    """

    def __init__(self, data_id, value):
        self.data_id = data_id
        self.value = value

    @staticmethod
    def _from(data):
        return Bytes(data_id=data.id.value, value=data.value.value)

    @staticmethod
    def from_payload(data_payload):
        """データのペイロードを Bytes オブジェクトに変換します。

        Args:
            data_payload(bytes): データのペイロード
        """
        id_length = int.from_bytes(data_payload[:1], byteorder="little")
        data_id = data_payload[1 : 1 + id_length].decode("utf-8")
        value = data_payload[1 + id_length :]
        return Bytes(data_id=data_id, value=value)

    def _to(self):
        return data.Bytes(
            id_length=field.Uint8(value=len(self.data_id)),
            id=field.String(value=self.data_id),
            value=field.Bytes(value=self.value),
        )

    @property
    def data(self):
        return self.value


class Basetime(Data):
    """基準時刻を表すデータオブジェクトです。

    Attributes:
        type (BasetimeType): 基準時刻種別
        basetime (pandas.Timestamp): 基準時刻
    """

    data_type = data.DataType.basetime
    """データタイプ
    """

    def __init__(self, type, basetime):
        self.type = type
        self.basetime = basetime

    def __str__(self) -> str:
        return "data_type: {data_type}\ntype: {type}\nbasetime: {basetime}".format(
            data_type=self.data_type.name, type=self.type, basetime=self.basetime
        )

    @staticmethod
    def _from(data):
        return Basetime(
            type=data.type.value,
            basetime=timeutils.unix2timestamp(
                unix_sec=data.basetime_sec.value, unix_nano=data.basetime_nsec.value
            ),
        )

    def _to(self):
        sec, nsec = timeutils.timestamp2unix(self.basetime)
        return data.Basetime(
            type=field.Uint8(value=self.type),
            basetime_sec=field.Uint32(value=sec),
            basetime_nsec=field.Uint32(value=nsec),
        )


data2data = {
    data.DataType.can.value: CAN,
    data.DataType.nmea.value: NMEA,
    data.DataType.general_sensor.value: GeneralSensor,
    data.DataType.controlpad.value: Controlpad,
    data.DataType.generic.value: Generic,
    data.DataType.jpeg.value: JPEG,
    data.DataType.float.value: Float,
    data.DataType.string.value: String,
    data.DataType.bytes.value: Bytes,
    data.DataType.int.value: Int,
    data.DataType.basetime.value: Basetime,
    data.DataType.h264.value: H264,
    data.DataType.aac.value: AAC,
    data.DataType.pcm.value: PCM,
}
