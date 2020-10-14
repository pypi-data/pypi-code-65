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
from enum import IntEnum

from . import _element, parser
from ._element import *
from .parser import element

__all__ = ["VERSION", "ResultCode", "Reader", "Writer"]

__all__.extend(_element.__all__)

VERSION = "v1.5.0"


class ResultCode(IntEnum):
    OK = element.RESULT_CODE_OK
    NG = element.RESULT_CODE_NG


class Reader(object):
    """エレメントを読み出すためのリーダーです。

    Args:
        rd (io.BufferedReader): リーダー
    """

    def __init__(self, rd):
        self.rd = parser.Reader(rd)

    def read_elem(self):
        """エレメントを読み出します。

        Return:
            Element: エレメント
        """

        pelem = self.rd.read_elem()

        if type(pelem) not in type2elem:
            raise NotImplementedError
        elem = type2elem[type(pelem)]._from(pelem)
        return elem


class Writer(object):
    """エレメントを書き込むためのライターです。

    Args:
        wr (io.BufferedWriter): ライター
    """

    def __init__(self, wr):
        self.wr = parser.Writer(wr)

    def write_elem(self, elem):
        """エレメントを読み出します。

        Args:
            elem (Element): エレメント
        """
        pelem = elem._to()
        self.wr.write_elem(pelem)


type2elem = {
    element.UpstreamSpecRequest: UpstreamSpecRequest,
    element.UpstreamSpecResponse: UpstreamSpecResponse,
    element.DownstreamSpecRequest: DownstreamSpecRequest,
    element.DownstreamSpecResponse: DownstreamSpecResponse,
    element.DownstreamFilterRequest: DownstreamFilterRequest,
    element.DownstreamFilterResponse: DownstreamFilterResponse,
    element.MeasurementIdRequest: MeasurementIDRequest,
    element.MeasurementIdResponse: MeasurementIDResponse,
    element.SosMarker: SOSMarker,
    element.EosMarker: EOSMarker,
    element.SectionAck: SectionAck,
    element.Unit: Unit,
}
