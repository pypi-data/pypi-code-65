#!/usr/bin/python3
# pylint: disable=missing-docstring

import sys
import argparse
import pkg_resources
from libkosciuszko import Kosciuszko

def main():
    version = pkg_resources.require("kosciuszko-utils")[0].version
    parser = argparse.ArgumentParser(description="create a new kosciuszko store")
    parser.add_argument("--version", action="version", version="%(prog)s {}".format(version))
    parser.add_argument("--gpg-id", nargs=1, help="GPG ID for the store")
    parser.add_argument("--store", nargs=1, help="Filename of the store (vault)")

    args = parser.parse_args(sys.argv[1:])
    gpg_id = vars(args)["gpg_id"]
    store = vars(args)["store"]

    kosciuszko = Kosciuszko(gpg_id[0], store[0])
    kosciuszko.new()
