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
import struct
import uuid

#
# fixed length fields
#


class Uuid(object):
    def __init__(self, value: uuid.UUID):
        self.value = value

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        bs = rd.read(16)
        if 0 == len(bs):
            raise EOFError

        value = uuid.UUID(bytes=bs)
        return Uuid(value=value)

    def _write_to(self, wr: io.BufferedWriter):
        bs = self.value.bytes
        wr.write(bs)

    def _length(self):
        return 16


class Uint8(object):
    def __init__(self, value: int):
        self.value = value

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        bs = rd.read(1)
        if 0 == len(bs):
            raise EOFError

        value = int.from_bytes(bs, "little")
        return Uint8(value=value)

    def _write_to(self, wr: io.BufferedWriter):
        bs = self.value.to_bytes(1, "little")
        wr.write(bs)

    def _length(self):
        return 1


class Uint16(object):
    def __init__(self, value: int):
        self.value = value

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        bs = rd.read(2)
        if 0 == len(bs):
            raise EOFError

        value = int.from_bytes(bs, "little")
        return Uint8(value=value)

    def _write_to(self, wr: io.BufferedWriter):
        bs = self.value.to_bytes(2, "little")
        wr.write(bs)

    def _length(self):
        return 2


class Uint24(object):
    def __init__(self, value: int):
        self.value = value

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        bs = rd.read(3)
        if 0 == len(bs):
            raise EOFError

        value = int.from_bytes(bs, "little")
        return Uint8(value=value)

    def _write_to(self, wr: io.BufferedWriter):
        bs = self.value.to_bytes(3, "little")
        wr.write(bs)

    def _length(self):
        return 3


class Uint32(object):
    def __init__(self, value: int):
        self.value = value

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        bs = rd.read(4)
        if 0 == len(bs):
            raise EOFError

        value = int.from_bytes(bs, "little")
        return Uint8(value=value)

    def _write_to(self, wr: io.BufferedWriter):
        bs = self.value.to_bytes(4, "little")
        wr.write(bs)

    def _length(self):
        return 4


class Uint40(object):
    def __init__(self, value: int):
        self.value = value

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        bs = rd.read(5)
        if 0 == len(bs):
            raise EOFError

        value = int.from_bytes(bs, "little")
        return Uint8(value=value)

    def _write_to(self, wr: io.BufferedWriter):
        bs = self.value.to_bytes(5, "little")
        wr.write(bs)

    def _length(self):
        return 5


class Float64(object):
    def __init__(self, value: float):
        self.value = value

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        bs = rd.read(8)
        if 0 == len(bs):
            raise EOFError

        value = struct.unpack("<d", bs)[0]
        return Float64(value=value)

    def _write_to(self, wr: io.BufferedWriter):
        bs = struct.pack("<d", self.value)
        wr.write(bs)

    def _length(self):
        return 8


class Int64(object):
    def __init__(self, value: int):
        self.value = value

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        bs = rd.read(8)
        if 0 == len(bs):
            raise EOFError

        value = struct.unpack("<q", bs)[0]
        return Int64(value=value)

    def _write_to(self, wr: io.BufferedWriter):
        bs = struct.pack("<q", self.value)
        wr.write(bs)

    def _length(self):
        return 8


#
# variable length fields
#


class Bytes(object):
    def __init__(self, value: bytes):
        self.value = value

    @staticmethod
    def _read_n_from(rd: io.BufferedReader, n: int):
        bs = rd.read(n)
        if 0 == len(bs):
            raise EOFError

        value = bs
        return Bytes(value=value)

    @staticmethod
    def _read_all_from(rd: io.BufferedReader):
        bs = rd.read()
        if 0 == len(bs):
            raise EOFError

        value = bs
        if len(value) == 0:
            raise EOFError
        return Bytes(value=value)

    def _write_to(self, wr: io.BufferedWriter):
        wr.write(self.value)

    def _length(self):
        return len(self.value)


class String(object):
    def __init__(self, value: str):
        self.value = value

    @staticmethod
    def _read_n_from(rd: io.BufferedReader, n: int):
        bs = rd.read(n)
        if 0 == len(bs):
            raise EOFError

        value = bs.decode("utf-8")
        return String(value=value)

    @staticmethod
    def _read_all_from(rd: io.BufferedReader):
        bs = rd.read()

        value = bs.decode("utf-8")
        return String(value=value)

    def _write_to(self, wr: io.BufferedWriter):
        wr.write(self.value.encode("utf-8"))

    def _length(self):
        return len(self.value.encode("utf-8"))


#
# custom fields
#


class VarUint8to32(object):
    def __init__(self, value, len):
        self.value = value
        self.len = len

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        bs = rd.read(1)
        if 0 == len(bs):
            raise EOFError

        if bs[0] & 3 == 3:
            bs_tmp = rd.read(3)
            if 0 == len(bs_tmp):
                raise EOFError
            bs += bs_tmp

            value = int.from_bytes(bs, "little") >> 2
            return VarUint8to32(value=value, len=4)

        if bs[0] & 3 == 2:
            bs_tmp = rd.read(2)
            if 0 == len(bs_tmp):
                raise EOFError
            bs += bs_tmp

            value = int.from_bytes(bs, "little") >> 2
            return VarUint8to32(value=value, len=3)

        if bs[0] & 3 == 1:
            bs_tmp = rd.read(1)
            if 0 == len(bs_tmp):
                raise EOFError
            bs += bs_tmp

            value = int.from_bytes(bs, "little") >> 2
            return VarUint8to32(value=value, len=2)

        value = int.from_bytes(bs, "little") >> 2
        return VarUint8to32(value=value, len=1)

    def _write_to(self, wr: io.BufferedWriter):
        if self.len == 4:
            bs = ((self.value << 2) + 3).to_bytes(4, "little")
            wr.write(bs)
            return

        if self.len == 3:
            bs = ((self.value << 2) + 2).to_bytes(3, "little")
            wr.write(bs)
            return

        if self.len == 2:
            bs = ((self.value << 2) + 1).to_bytes(2, "little")
            wr.write(bs)
            return

        bs = ((self.value << 2) + 0).to_bytes(1, "little")
        wr.write(bs)

    def _length(self):
        self.len


class VarUint16to24(object):
    def __init__(self, value, len):
        self.value = value
        self.len = len

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        bs = rd.read(2)
        if 0 == len(bs):
            raise EOFError

        if bs[0] & 1 == 1:
            bs_tmp = rd.read(1)
            if 0 == len(bs_tmp):
                raise EOFError
            bs += bs_tmp

            value = int.from_bytes(bs, "little") >> 1
            return VarUint16to24(value=value, len=3)

        value = int.from_bytes(bs, "little") >> 1
        return VarUint16to24(value=value, len=2)

    def _write_to(self, wr: io.BufferedWriter):
        if self.len == 3:
            bs = ((self.value << 1) + 1).to_bytes(3, "little")
            wr.write(bs)
            return

        bs = ((self.value << 1) + 0).to_bytes(2, "little")
        wr.write(bs)

    def _length(self):
        return self.len


class VarUint16to32(object):
    def __init__(self, value, len):
        self.value = value
        self.len = len

    @staticmethod
    def _read_from(rd: io.BufferedReader):
        bs = rd.read(2)
        if 0 == len(bs):
            raise EOFError

        if bs[0] & 3 == 2:
            bs_tmp = rd.read(2)
            if 0 == len(bs_tmp):
                raise EOFError
            bs += bs_tmp

            value = int.from_bytes(bs, "little") >> 2
            return VarUint16to32(value=value, len=4)

        if bs[0] & 3 == 1:
            bs_tmp = rd.read(1)
            if 0 == len(bs_tmp):
                raise EOFError
            bs += bs_tmp

            value = int.from_bytes(bs, "little") >> 2
            return VarUint16to32(value=value, len=3)

        value = int.from_bytes(bs, "little") >> 2
        return VarUint16to32(value=value, len=2)

    def _write_to(self, wr: io.BufferedWriter):
        if self.len == 4:
            bs = ((self.value << 2) + 2).to_bytes(4, "little")
            wr.write(bs)
            return

        if self.len == 3:
            bs = ((self.value << 2) + 1).to_bytes(3, "little")
            wr.write(bs)
            return

        bs = ((self.value << 2) + 0).to_bytes(2, "little")
        wr.write(bs)

    def _length(self):
        return self.len
