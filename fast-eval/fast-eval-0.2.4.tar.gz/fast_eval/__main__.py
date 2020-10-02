#!/usr/bin/env python3
import argparse
from fast_eval.util import FastEval
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config",
                        help="path of json config file")
    parser.add_argument("archive_path",
                        help="path of archive from arche")
    parser.add_argument("--ws",
                        help="where to build workspace")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    fe = FastEval(parser.parse_args())
