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

import string

# Charsets for code 39
REF = (
    tuple(string.digits)
    + tuple(string.ascii_uppercase)
    + ("-", ".", " ", "$", "/", "+", "%")
)
B = "1"
E = "0"
CODES = (
    "101000111011101",
    "111010001010111",
    "101110001010111",
    "111011100010101",
    "101000111010111",
    "111010001110101",
    "101110001110101",
    "101000101110111",
    "111010001011101",
    "101110001011101",
    "111010100010111",
    "101110100010111",
    "111011101000101",
    "101011100010111",
    "111010111000101",
    "101110111000101",
    "101010001110111",
    "111010100011101",
    "101110100011101",
    "101011100011101",
    "111010101000111",
    "101110101000111",
    "111011101010001",
    "101011101000111",
    "111010111010001",
    "101110111010001",
    "101010111000111",
    "111010101110001",
    "101110101110001",
    "101011101110001",
    "111000101010111",
    "100011101010111",
    "111000111010101",
    "100010111010111",
    "111000101110101",
    "100011101110101",
    "100010101110111",
    "111000101011101",
    "100011101011101",
    "100010001000101",
    "100010001010001",
    "100010100010001",
    "101000100010001",
)

EDGE = "100010111011101"
MIDDLE = "0"

# MAP for assigning every symbol (REF) to (reference number, barcode)
MAP = dict(zip(REF, enumerate(CODES)))
