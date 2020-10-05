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
import io
from enum import Enum

from . import field


class DataType(Enum):
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


def type2data(data_type):
    if data_type == DataType.can.value:
        return CAN
    if data_type == DataType.can_bulk.value:
        return CanBulk
    if data_type == DataType.nmea.value:
        return NMEA
    if data_type == DataType.general_sensor.value:
        return GeneralSensor
    if data_type == DataType.general_sensor_bulk.value:
        return GeneralSensorBulk
    if data_type == DataType.jpeg.value:
        return JPEG
    if data_type == DataType.controlpad.value:
        return Controlpad
    if data_type == DataType.mavlink.value:
        return Mavlink
    if data_type == DataType.generic.value:
        return Generic
    if data_type == DataType.basetime.value:
        return Basetime
    if data_type == DataType.string.value:
        return String
    if data_type == DataType.float.value:
        return Float
    if data_type == DataType.int.value:
        return Int
    if data_type == DataType.bytes.value:
        return Bytes
    if data_type == DataType.h264.value:
        return H264
    if data_type == DataType.aac.value:
        return AAC
    if data_type == DataType.pcm.value:
        return PCM
    raise NotImplementedError


def data2type(data):
    if type(data) == CAN:
        return DataType.can.value
    if type(data) == CanBulk:
        return DataType.can_bulk.value
    if type(data) == NMEA:
        return DataType.nmea.value
    if type(data) == GeneralSensor:
        return DataType.general_sensor.value
    if type(data) == GeneralSensorBulk:
        return DataType.general_sensor_bulk.value
    if type(data) == JPEG:
        return DataType.jpeg.value
    if type(data) == Controlpad:
        return DataType.controlpad.value
    if type(data) == Mavlink:
        return DataType.mavlink.value
    if type(data) == Generic:
        return DataType.generic.value
    if type(data) == Basetime:
        return DataType.basetime.value
    if type(data) == String:
        return DataType.string.value
    if type(data) == Float:
        return DataType.float.value
    if type(data) == Int:
        return DataType.int.value
    if type(data) == Bytes:
        return DataType.bytes.value
    if type(data) == H264:
        return DataType.h264.value
    if type(data) == AAC:
        return DataType.aac.value
    if type(data) == PCM:
        return DataType.pcm.value
    raise NotImplementedError


class CAN(object):
    def __init__(self, id, dlc, data):
        self.id = id
        self.dlc = dlc
        self.data = data

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        id = field.Uint32._read_from(rd)
        dlc = field.Uint8._read_from(rd)
        data = field.Bytes._read_n_from(rd, dlc.value)
        return CAN(id=id, dlc=dlc, data=data)

    def _write_to(self, wr: io.BufferedWriter):
        self.id._write_to(wr)
        self.dlc._write_to(wr)
        self.data._write_to(wr)

    def _length(self):
        l = 0
        l += self.id._length()
        l += self.dlc._length()
        l += self.data._length()
        return l


class CanBulk(object):
    def __init__(self, list):
        self.list = list

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        list = []
        while True:
            try:
                list.append(CanBulkEach._read_from(rd))
            except EOFError:
                break
        return CanBulk(list=list)

    def _write_to(self, wr: io.BufferedWriter):
        [x._write_to(wr) for x in self.list]

    def _length(self):
        l = 0
        l += sum([v._length() for v in self.list])
        return l


class CanBulkEach(object):
    def __init__(self, id, dlc, count, usec, data):
        self.id = id
        self.dlc = dlc
        self.count = count
        self.usec = usec
        self.data = data

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        id = field.Uint32._read_from(rd)
        dlc = field.Uint8._read_from(rd)
        count = field.Uint16._read_from(rd)
        usec = [field.Uint24._read_from(rd) for i in range(count.value)]
        data = [field.Bytes._read_n_from(rd, dlc.value) for i in range(count.value)]
        return CanBulkEach(id=id, dlc=dlc, count=count, usec=usec, data=data)

    def _write_to(self, wr: io.BufferedWriter):
        self.id._write_to(wr)
        self.dlc._write_to(wr)
        self.count._write_to(wr)
        [x._write_to(wr) for x in self.usec]
        [x._write_to(wr) for x in self.data]

    def _length(self):
        l = 0
        l += self.id._length()
        l += self.dlc._length()
        l += self.count._length()
        l += sum([v._length() for v in self.usec])
        l += sum([v._length() for v in self.data])
        return l


class NMEA(object):
    def __init__(self, string):
        self.string = string

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        string = field.String._read_all_from(rd)
        return NMEA(string=string)

    def _write_to(self, wr: io.BufferedWriter):
        self.string._write_to(wr)

    def _length(self):
        l = 0
        l += self.string._length()
        return l


class GeneralSensor(object):
    def __init__(self, id, data):
        self.id = id
        self.data = data

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        id = field.Uint16._read_from(rd)
        data = field.Bytes._read_all_from(rd)
        return GeneralSensor(id=id, data=data)

    def _write_to(self, wr: io.BufferedWriter):
        self.id._write_to(wr)
        self.data._write_to(wr)

    def _length(self):
        l = 0
        l += self.id._length()
        l += self.data._length()
        return l


class GeneralSensorBulk(object):
    def __init__(self, list):
        self.list = list

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        list = []
        while True:
            try:
                list.append(GeneralSensorBulkEach._read_from(rd))
            except EOFError:
                break
        return GeneralSensorBulk(list=list)

    def _write_to(self, wr: io.BufferedWriter):
        [x._write_to(wr) for x in self.list]

    def _length(self):
        l = 0
        l += sum([v._length() for v in self.list])
        return l


class GeneralSensorBulkEach(object):
    def __init__(self, id, length, count, usec, data):
        self.id = id
        self.length = length
        self.count = count
        self.usec = usec
        self.data = data

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        id = field.Uint16._read_from(rd)
        length = field.Uint8._read_from(rd)
        count = field.Uint16._read_from(rd)
        usec = [field.Uint24._read_from(rd) for i in range(count.value)]
        data = [field.Bytes._read_n_from(rd, length.value) for i in range(count.value)]
        return GeneralSensorBulkEach(
            id=id, length=length, count=count, usec=usec, data=data
        )

    def _write_to(self, wr: io.BufferedWriter):
        self.id._write_to(wr)
        self.length._write_to(wr)
        self.count._write_to(wr)
        [x._write_to(wr) for x in self.usec]
        [x._write_to(wr) for x in self.data]

    def _length(self):
        l = 0
        l += self.id._length()
        l += self.length._length()
        l += self.count._length()
        l += sum([v._length() for v in self.usec])
        l += sum([v._length() for v in self.data])
        return l


class JPEG(object):
    def __init__(self, data):
        self.data = data

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        data = field.Bytes._read_all_from(rd)
        return JPEG(data=data)

    def _write_to(self, wr: io.BufferedWriter):
        self.data._write_to(wr)

    def _length(self):
        l = 0
        l += self.data._length()
        return l


class H264(object):
    def __init__(self, type_id, data):
        self.type_id = type_id
        self.data = data

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        type_id = field.Uint8._read_from(rd)
        data = field.Bytes._read_all_from(rd)
        return H264(type_id=type_id, data=data)

    def _write_to(self, wr: io.BufferedWriter):
        self.type_id._write_to(wr)
        self.data._write_to(wr)

    def _length(self):
        l = 0
        l += self.type_id._length()
        l += self.data._length()
        return l


class AAC(object):
    def __init__(self, data):
        self.data = data

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        data = field.Bytes._read_all_from(rd)
        return AAC(data=data)

    def _write_to(self, wr: io.BufferedWriter):
        self.data._write_to(wr)

    def _length(self):
        l = 0
        l += self.data._length()
        return l


class PCM(object):
    def __init__(self, format_id, channels, sample_rate, bit_per_sample, data):
        self.format_id = format_id
        self.channels = channels
        self.sample_rate = sample_rate
        self.bit_per_sample = bit_per_sample
        self.data = data

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        format_id = field.Uint16._read_from(rd)
        channels = field.Uint16._read_from(rd)
        sample_rate = field.Uint32._read_from(rd)
        bit_per_sample = field.Uint16._read_from(rd)
        data = field.Bytes._read_all_from(rd)
        return PCM(
            format_id=format_id,
            channels=channels,
            sample_rate=sample_rate,
            bit_per_sample=bit_per_sample,
            data=data,
        )

    def _write_to(self, wr: io.BufferedWriter):
        self.format_id._write_to(wr)
        self.channels._write_to(wr)
        self.sample_rate._write_to(wr)
        self.bit_per_sample._write_to(wr)
        self.data._write_to(wr)

    def _length(self):
        l = 0
        l += self.format_id._length()
        l += self.channels._length()
        l += self.sample_rate._length()
        l += self.bit_per_sample._length()
        l += self.data._length()


class Controlpad(object):
    def __init__(self, id, data):
        self.id = id
        self.data = data

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        id = field.Uint8._read_from(rd)
        data = field.Bytes._read_all_from(rd)
        return Controlpad(id=id, data=data)

    def _write_to(self, wr: io.BufferedWriter):
        self.id._write_to(wr)
        self.data._write_to(wr)

    def _length(self):
        l = 0
        l += self.id._length()
        l += self.data._length()
        return l


class Mavlink(object):
    def __init__(
        self,
        packet_start_sign,
        payload_length,
        packet_sequence,
        system_id,
        component_id,
        message_id,
        data,
        checksum,
    ):
        self.packet_start_sign = packet_start_sign
        self.payload_length = payload_length
        self.packet_sequence = packet_sequence
        self.system_id = system_id
        self.component_id = component_id
        self.message_id = message_id
        self.data = data
        self.checksum = checksum

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        packet_start_sign = field.Uint8._read_from(rd)
        payload_length = field.Uint8._read_from(rd)
        packet_sequence = field.Uint8._read_from(rd)
        system_id = field.Uint8._read_from(rd)
        component_id = field.Uint8._read_from(rd)
        message_id = field.Uint8._read_from(rd)
        data = field.Bytes._read_n_from(rd, payload_length.value)
        checksum = field.Uint8._read_from(rd)
        return Mavlink(
            packet_start_sign=packet_start_sign,
            payload_length=payload_length,
            packet_sequence=packet_sequence,
            system_id=system_id,
            component_id=component_id,
            message_id=message_id,
            data=data,
            checksum=checksum,
        )

    def _write_to(self, wr: io.BufferedWriter):
        self.packet_start_sign._write_to(wr)
        self.payload_length._write_to(wr)
        self.packet_sequence._write_to(wr)
        self.system_id._write_to(wr)
        self.component_id._write_to(wr)
        self.message_id._write_to(wr)
        self.data._write_to(wr)
        self.checksum._write_to(wr)

    def _length(self):
        l = 0
        l += self.packet_start_sign._length()
        l += self.payload_length._length()
        l += self.packet_sequence._length()
        l += self.system_id._length()
        l += self.component_id._length()
        l += self.message_id._length()
        l += self.data._length()
        l += self.checksum._length()
        return l


class Generic(object):
    def __init__(self, id, data):
        self.id = id
        self.data = data

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        id = field.Uint32._read_from(rd)
        data = field.Bytes._read_all_from(rd)
        return Generic(id=id, data=data)

    def _write_to(self, wr: io.BufferedWriter):
        self.id._write_to(wr)
        self.data._write_to(wr)

    def _length(self):
        l = 0
        l += self.id._length()
        l += self.data._length()
        return l


class Float(object):
    def __init__(self, id_length, id, value):
        self.id_length = id_length
        self.id = id
        self.value = value

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        id_length = field.Uint8._read_from(rd)
        id = field.String._read_n_from(rd, id_length.value)
        value = field.Float64._read_from(rd)
        return Float(id_length=id_length, id=id, value=value)

    def _write_to(self, wr: io.BufferedWriter):
        self.id_length._write_to(wr)
        self.id._write_to(wr)
        self.value._write_to(wr)

    def _length(self):
        l = 0
        l += self.id_length._length()
        l += self.id._length()
        l += self.value._length()
        return l


class String(object):
    def __init__(self, id_length, id, value):
        self.id_length = id_length
        self.id = id
        self.value = value

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        id_length = field.Uint8._read_from(rd)
        id = field.String._read_n_from(rd, id_length.value)
        value = field.String._read_all_from(rd)
        return String(id_length=id_length, id=id, value=value)

    def _write_to(self, wr: io.BufferedWriter):
        self.id_length._write_to(wr)
        self.id._write_to(wr)
        self.value._write_to(wr)

    def _length(self):
        l = 0
        l += self.id_length._length()
        l += self.id._length()
        l += self.value._length()
        return l


class Int(object):
    def __init__(self, id_length, id, value):
        self.id_length = id_length
        self.id = id
        self.value = value

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        id_length = field.Uint8._read_from(rd)
        id = field.String._read_n_from(rd, id_length.value)
        value = field.Int64._read_from(rd)
        return Int(id_length=id_length, id=id, value=value)

    def _write_to(self, wr: io.BufferedWriter):
        self.id_length._write_to(wr)
        self.id._write_to(wr)
        self.value._write_to(wr)

    def _length(self):
        l = 0
        l += self.id_length._length()
        l += self.id._length()
        l += self.value._length()
        return l


class Bytes(object):
    def __init__(self, id_length, id, value):
        self.id_length = id_length
        self.id = id
        self.value = value

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        id_length = field.Uint8._read_from(rd)
        id = field.String._read_n_from(rd, id_length.value)
        value = field.Bytes._read_all_from(rd)
        return Bytes(id_length=id_length, id=id, value=value)

    def _write_to(self, wr: io.BufferedWriter):
        self.id_length._write_to(wr)
        self.id._write_to(wr)
        self.value._write_to(wr)

    def _length(self):
        l = 0
        l += self.id_length._length()
        l += self.id._length()
        l += self.value._length()
        return l


class Basetime(object):
    def __init__(self, type, basetime_sec, basetime_nsec):
        self.type = type
        self.basetime_sec = basetime_sec
        self.basetime_nsec = basetime_nsec

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        type = field.Uint8._read_from(rd)
        basetime_sec = field.Uint32._read_from(rd)
        basetime_nsec = field.Uint32._read_from(rd)
        return Basetime(
            type=type, basetime_sec=basetime_sec, basetime_nsec=basetime_nsec
        )

    def _write_to(self, wr: io.BufferedWriter):
        self.type._write_to(wr)
        self.basetime_sec._write_to(wr)
        self.basetime_nsec._write_to(wr)

    def _length(self):
        l = 0
        l += self.type._length()
        l += self.basetime_sec._length()
        l += self.basetime_nsec._length()
        return l
