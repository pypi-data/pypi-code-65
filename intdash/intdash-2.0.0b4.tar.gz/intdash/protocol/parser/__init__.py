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

from . import element, field

PREAMBLE = int.from_bytes(b"\xaa", "little")


class Reader(object):
    def __init__(self, rd: io.BufferedReader):
        rd.seek(0)
        self.rd = rd

    def read_elem(self):
        h = element.CommonHeader._read_from(self.rd)
        if h.preamble.value != PREAMBLE:
            raise ValueError
        return element.type2elem(h.elem_type.value)._read_from(self.rd)


class Writer(object):
    def __init__(self, wr: io.BufferedWriter):
        self.wr = wr

    def write_elem(self, elem):
        h = element.CommonHeader(
            preamble=field.Uint8(value=element.PREAMBLE),
            elem_type=field.Uint8(value=element.elem2type(elem)),
        )
        h._write_to(self.wr)
        elem._write_to(self.wr)
        self.wr.flush()
