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
from argparse import ArgumentParser

import ldb.inventory.barcode
from ldb.inventory.barcode.version import version
from ldb.inventory.barcode.writer import ImageWriter
from ldb.inventory.barcode.writer import SVGWriter

IMG_FORMATS = ("BMP", "GIF", "JPEG", "MSP", "PCX", "PNG", "TIFF", "XBM")


def list_types(args, parser=None):
    print("\npython-barcode available barcode formats:")
    print(", ".join(ldb.inventory.barcode.PROVIDED_BARCODES))
    print("\n")
    print("Available image formats")
    print("Standard: svg")
    if ImageWriter is not None:
        print("Pillow:", ", ".join(IMG_FORMATS))
    else:
        print("Pillow: disabled")
    print("\n")


def create_barcode(args, parser):
    args.type = args.type.upper()
    if args.type != "SVG" and args.type not in IMG_FORMATS:
        parser.error(
            "Unknown type {type}. Try list action for available types.".format(
                type=args.type
            )
        )
    args.barcode = args.barcode.lower()
    if args.barcode not in ldb.inventory.barcode.PROVIDED_BARCODES:
        parser.error(
            "Unknown barcode {bc}. Try list action for available barcodes.".format(
                bc=args.barcode
            )
        )
    if args.type != "SVG":
        opts = {"format": args.type}
        writer = ImageWriter()
    else:
        opts = {"compress": args.compress}
        writer = SVGWriter()
    out = os.path.normpath(os.path.abspath(args.output))
    name = ldb.inventory.barcode.generate(args.barcode, args.code, writer, out, opts, args.text)
    print("New barcode saved as {}.".format(name))


def main():
    msg = []
    if ImageWriter is None:
        msg.append("Image output disabled (Pillow not found), --type option disabled.")
    else:
        msg.append(
            "Image output enabled, use --type option to give image "
            "format (png, jpeg, ...)."
        )
    parser = ArgumentParser(
        description="Create standard barcodes via cli.", epilog=" ".join(msg)
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + version
    )
    subparsers = parser.add_subparsers(title="Actions")
    create_parser = subparsers.add_parser(
        "create", help="Create a barcode with the given options."
    )
    create_parser.add_argument("code", help="Code to render as barcode.")
    create_parser.add_argument(
        "output", help="Filename for output without extension, e. g. mybarcode."
    )
    create_parser.add_argument(
        "-c",
        "--compress",
        action="store_true",
        help="Compress output, only recognized if type is svg.",
    )
    create_parser.add_argument(
        "-b", "--barcode", help="Barcode to use [default: %(default)s]."
    )
    create_parser.add_argument("--text", help="Text to show under the barcode.")
    if ImageWriter is not None:
        create_parser.add_argument(
            "-t", "--type", help="Type of output [default: %(default)s]."
        )
    list_parser = subparsers.add_parser(
        "list", help="List available image and code types."
    )
    list_parser.set_defaults(func=list_types)
    create_parser.set_defaults(
        type="svg", compress=False, func=create_barcode, barcode="code39", text=None
    )
    args = parser.parse_args()
    try:
        func = args.func
    except AttributeError:
        parser.error("You need to tell me what to do.")
    else:
        func(args, parser)


if __name__ == "__main__":
    main()
