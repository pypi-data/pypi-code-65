#!/usr/bin/python3
# pylint: disable=missing-docstring

import sys
import argparse
from pathlib import Path
import pkg_resources
import uuid
from libkosciuszko import Kosciuszko

def main():
    version = pkg_resources.require("kosciuszko-utils")[0].version
    parser = argparse.ArgumentParser(description="add a file to a kosciuszko store")
    parser.add_argument("--version", action="version", version="%(prog)s {}".format(version))
    parser.add_argument("--gpg-id", nargs=1, help="GPG ID for the store")
    parser.add_argument("--store", nargs=1, help="Filename of the store (vault)")
    parser.add_argument("--filename", nargs='?', help="name of file to add")
    parser.add_argument("file", nargs='?', help="file to add (optional; otherwise read from stdin)")

    args = parser.parse_args(sys.argv[1:])
    gpg_id = vars(args)["gpg_id"]
    store = vars(args)["store"]
    fileinput = vars(args)["file"]
    filename = vars(args)["filename"]

    kosciuszko = Kosciuszko(gpg_id[0], store[0])

    if filename is not None and fileinput is not None:
        # Read the file and  store with filename
        with open(fileinput, 'rb') as fh:
            data = fh.read()
        kosciuszko.addfile(filename, data)
    if not filename is not None and fileinput is not None:
        # Read the file and store without changing the filename
        with open(fileinput, 'rb') as fh:
            data = fh.read()
        filename = Path(fileinput)
        filename = filename.name
        kosciuszko.addfile(filename, data)
    if filename is not None and not fileinput is not None:
        # Read from stdin and store with filename
        with open('/dev/stdin') as fh:
            data = fh.read()
        if isinstance(data, str):
            data = data.encode('utf-8')
        kosciuszko.addfile(filename, data)
    if not filename is not None and not fileinput is not None:
        # Read from stdin and store with random filename
        filename = (uuid.uuid4())
        with open('/dev/stdin', 'rb') as fh:
            data = fh.read()
        if isinstance(data, str):
            data = data.encode('utf-8')
        kosciuszko.addfile(filename, data)
