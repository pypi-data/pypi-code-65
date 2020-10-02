#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, argparse
from ..libs.LineNotify import line_notify

command_name = os.path.basename(__file__).split('.', 1)[0].replace("_", ":")


def register(parser, subparsers, **kwargs):

    def handler(args):
        if args.token is None or args.msg is None:
            print(parser.parse_args([command_name, '--help']))
            return
        res = line_notify(args.token, args.msg, args.file)
        print(res.text)

    subcommand = subparsers.add_parser(command_name, help='line notify.')
    subcommand.add_argument('-t',
                            '--token',
                            type=str,
                            help='token',
                            default=os.getenv('LINE_NOTIFY_TOKEN'),
                            required=False)
    subcommand.add_argument('-m',
                            '--msg',
                            type=str,
                            help='message',
                            required=True)
    subcommand.add_argument('-f',
                            '--file',
                            type=str,
                            help='image file',
                            required=False)
    subcommand.set_defaults(handler=handler)
