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

from ldb.inventory.barcode import EAN13
from ldb.inventory.barcode.writer import PdfWriter, pdf_canvas, pdf_black
from ldb.inventory.barcode.writer import ImageWriter
from ldb.inventory.barcode.writer import SVGWriter


PATH = os.path.dirname(os.path.abspath(__file__))
TESTPATH = os.path.join(PATH, "test_outputs")

if pdf_canvas:
    def test_saving_pdf():
        writer = PdfWriter(f"{TESTPATH}/ean13-with-transparent-bg.pdf")
        EAN13(str(100000011111), writer=writer).render()

if ImageWriter:

    def test_saving_image_to_byteio():
        rv = BytesIO()
        EAN13(str(100000902922), writer=ImageWriter()).write(rv)

        with open(f"{TESTPATH}/somefile.jpeg", "wb") as f:
            EAN13("100000011111", writer=ImageWriter()).write(f)

    def test_saving_rgba_image():
        rv = BytesIO()
        EAN13(str(100000902922), writer=ImageWriter()).write(rv)

        with open(f"{TESTPATH}/ean13-with-transparent-bg.png", "wb") as f:
            writer = ImageWriter(mode="RGBA")

            EAN13("100000011111", writer=writer).write(
                f, options={"background": "rgba(255,0,0,0)"}
            )


def test_saving_svg_to_byteio():
    rv = BytesIO()
    EAN13(str(100000902922), writer=SVGWriter()).write(rv)

    with open(f"{TESTPATH}/somefile.svg", "wb") as f:
        EAN13("100000011111", writer=SVGWriter()).write(f)
