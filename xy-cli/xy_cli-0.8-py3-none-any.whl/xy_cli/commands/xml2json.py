#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ..libs.xml2json import xml2json

import sys, os, json
import pprint
import argparse

command_name = os.path.basename(__file__).split('.', 1)[0].replace("_", ":")


def main(args):
    print(xml2json(args.file))

def register(parser, subparsers, **kwargs):

    def handler(args):
        if args.file is None:
            print(parser.parse_args([command_name, '--help']))
            return
        if args.file:
            main(args)

    subcommand = subparsers.add_parser(command_name,
                                       help='xml to json')
    subcommand.add_argument('-f',
                            '--file',
                            type=str,
                            default=None,
                            help='xml file',
                            required=True)
    subcommand.set_defaults(handler=handler)
