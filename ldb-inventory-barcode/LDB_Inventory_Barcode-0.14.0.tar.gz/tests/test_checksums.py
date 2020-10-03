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

from ldb.inventory.barcode import get_barcode


def test_code39_checksum():
    code39 = get_barcode("code39", "Code39")
    assert "CODE39W" == code39.get_fullcode()


def test_pzn_checksum():
    pzn = get_barcode("pzn", "103940")
    assert "PZN-1039406" == pzn.get_fullcode()


def test_ean13_checksum():
    ean = get_barcode("ean13", "400614457735")
    assert "4006144577350" == ean.get_fullcode()


def test_ean8_checksum():
    ean = get_barcode("ean8", "6032299")
    assert "60322999" == ean.get_fullcode()


def test_jan_checksum():
    jan = get_barcode("jan", "491400614457")
    assert "4914006144575" == jan.get_fullcode()


def test_ean14_checksum():
    ean = get_barcode("ean14", "1234567891258")
    assert "12345678912589" == ean.get_fullcode()


def test_isbn10_checksum():
    isbn = get_barcode("isbn10", "376926085")
    assert "3769260856" == isbn.isbn10


def test_isbn13_checksum():
    isbn = get_barcode("isbn13", "978376926085")
    assert "9783769260854" == isbn.get_fullcode()


def test_gs1_128_checksum():
    gs1_128 = get_barcode("gs1_128", "00376401856400470087")
    assert "00376401856400470087" == gs1_128.get_fullcode()
