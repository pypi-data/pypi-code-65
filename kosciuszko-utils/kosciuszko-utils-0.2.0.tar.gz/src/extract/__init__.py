#!/usr/bin/python3
# pylint: disable=missing-docstring

import os
import sys
import argparse
from pathlib import Path
import pkg_resources
from libkosciuszko import Kosciuszko

def main():
    version = pkg_resources.require("kosciuszko-utils")[0].version
    parser = argparse.ArgumentParser(description="extract a single file from a kosciuszko store")
    parser.add_argument("--version", action="version", version="%(prog)s {}".format(version))
    parser.add_argument("--gpg-id", nargs=1, help="GPG ID for the store")
    parser.add_argument("--store", nargs=1, help="Filename of the store (vault)")
    parser.add_argument("--output", nargs='?', help="directory to write to (otherwise squashfs-root)")

    args = parser.parse_args(sys.argv[1:])
    gpg_id = vars(args)["gpg_id"]
    store = vars(args)["store"]
    output = vars(args)["output"]

    kosciuszko = Kosciuszko(gpg_id[0], store[0])
    ls = kosciuszko.list()

    if not output is not None:
        output = "squashfs-root"

    for filename in ls:
        if filename == "squashfs-root":
            os.makedirs(output, exist_ok=True)
            continue
        filename = Path(filename).name
        data = kosciuszko.getfile(filename)
        with open(f"{output}/{filename}", 'ab') as fh:
            fh.write(data)
