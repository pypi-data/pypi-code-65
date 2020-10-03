#!/usr/bin/python3
# pylint: disable=missing-docstring

import os
import sys
import argparse
import pkg_resources
from libkosciuszko import Kosciuszko

def main():
    version = pkg_resources.require("kosciuszko-utils")[0].version
    parser = argparse.ArgumentParser(description="extract a single file from a kosciuszko store")
    parser.add_argument("--version", action="version", version="%(prog)s {}".format(version))
    parser.add_argument("--gpg-id", nargs=1, help="GPG ID for the store")
    parser.add_argument("--store", nargs=1, help="Filename of the store (vault)")
    parser.add_argument("--output", nargs='?', help="File to write to (otherwise stdout)")
    parser.add_argument("filename")

    args = parser.parse_args(sys.argv[1:])
    gpg_id = vars(args)["gpg_id"]
    store = vars(args)["store"]
    filename = vars(args)["filename"]
    output = vars(args)["output"]

    kosciuszko = Kosciuszko(gpg_id[0], store[0])
    data = kosciuszko.getfile(filename)

    if output is not None:
        with open(output, 'ab') as fh:
            fh.write(data)
    else:
        fp = os.fdopen(sys.stdout.fileno(), 'wb')
        fp.write(data)
        fp.flush()
