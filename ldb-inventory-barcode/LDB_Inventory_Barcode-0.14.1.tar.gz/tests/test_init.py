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

import os
from io import BytesIO

import pytest

import ldb.inventory.barcode
from ldb.inventory.barcode.writer import SVGWriter

PATH = os.path.dirname(os.path.abspath(__file__))
TESTPATH = os.path.join(PATH, "test_outputs")


def test_generate_without_output():
    with pytest.raises(TypeError, match="'output' cannot be None"):
        ldb.inventory.barcode.generate("ean13", "123455559121112")


def test_generate_with_file():
    with open(os.path.join(TESTPATH, "generate_with_file.jpeg"), "wb") as f:
        ldb.inventory.barcode.generate("ean13", "123455559121112", output=f)


def test_generate_with_filepath():
    # FIXME: extension is added to the filepath even if you include it.
    rv = ldb.inventory.barcode.generate(
        "ean13",
        "123455559121112",
        output=os.path.join(TESTPATH, "generate_with_filepath"),
    )
    assert rv == os.path.abspath(os.path.join(TESTPATH, "generate_with_filepath.svg"))


def test_generate_with_file_and_writer():
    with open(os.path.join(TESTPATH, "generate_with_file_and_writer.jpeg"), "wb") as f:
        ldb.inventory.barcode.generate("ean13", "123455559121112", output=f, writer=SVGWriter())


def test_generate_with_bytesio():
    bio = BytesIO()
    ldb.inventory.barcode.generate("ean13", "123455559121112", output=bio)
    # XXX: File is not 100% deterministic; needs to be addressed at some point.
    # assert len(bio.getvalue()) == 6127
