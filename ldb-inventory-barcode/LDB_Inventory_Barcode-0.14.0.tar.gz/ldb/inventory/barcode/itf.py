# Copyright 2020 Alex Orange 
# 
# This file is part of LDB Inventory Barcode.
# 
# LDB Inventory Barcode is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# LDB Inventory Barcode is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with LDB Inventory Barcode.  If not, see
# <https://www.gnu.org/licenses/>.
#
# This code derives from python-barcode
#
# Copyright (c) 2017-2020 Hugo Osvaldo Barrera <hugo@barrera.io>, et al
# Copyright (c) 2010-2013 Thorsten Weimann
#
# python-barcode is licensed under the MIT License, contained in MIT-LICENSE.
# All modifications to python-barcode are licensed as described above. If you
# want MIT Licensed code, just get the original from python-barcode.

"""Module: barcode.itf

:Provided barcodes: Interleaved 2 of 5
"""
__docformat__ = "restructuredtext en"

from ldb.inventory.barcode.base import Barcode
from ldb.inventory.barcode.charsets import itf
from ldb.inventory.barcode.errors import IllegalCharacterError

MIN_SIZE = 0.2
MIN_QUIET_ZONE = 6.4


class ITF(Barcode):
    """Initializes a new ITF instance.

    :parameters:
        code : String
            ITF (Interleaved 2 of 5) numeric string
        writer : barcode.writer Instance
            The writer to render the barcode (default: SVGWriter).
        narrow: Integer
            Width of the narrow elements (default: 2)
        wide: Integer
            Width of the wide elements (default: 5)
            wide/narrow must be in the range 2..3
    """

    name = "ITF"

    def __init__(self, code, writer=None, narrow=2, wide=5):
        if not code.isdigit():
            raise IllegalCharacterError("ITF code can only contain numbers.")
        # Length must be even, prepend 0 if necessary
        if len(code) % 2 != 0:
            code = "0" + code
        self.code = code
        self.writer = writer or Barcode.default_writer()
        self.narrow = narrow
        self.wide = wide

    def __str__(self):
        return self.code

    def get_fullcode(self):
        return self.code

    def build(self):
        data = itf.START
        for i in range(0, len(self.code), 2):
            bars_digit = int(self.code[i])
            spaces_digit = int(self.code[i + 1])
            for j in range(5):
                data += itf.CODES[bars_digit][j].upper()
                data += itf.CODES[spaces_digit][j].lower()
        data += itf.STOP
        raw = ""
        for e in data:
            if e == "W":
                raw += "1" * self.wide
            if e == "w":
                raw += "0" * self.wide
            if e == "N":
                raw += "1" * self.narrow
            if e == "n":
                raw += "0" * self.narrow
        return [raw]

    def render(self, writer_options, text=None):
        options = {
            "module_width": MIN_SIZE / self.narrow,
            "quiet_zone": MIN_QUIET_ZONE,
        }
        options.update(writer_options or {})
        return Barcode.render(self, options, text)
