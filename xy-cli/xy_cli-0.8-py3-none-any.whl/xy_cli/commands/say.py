#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, argparse
from ..libs.tts import g_tts
import tempfile


command_name = os.path.basename(__file__).split('.', 1)[0].replace("_", ":")


def main(args):
    if args.sentence:
        g_tts(args.sentence, args.tmpdir, args.lang, args.engine)

def register(parser, subparsers, **kwargs):

    def handler(args):
        if args.sentence is None:
            print(parser.parse_args([command_name, '--help']))
            return
        if args.sentence:
            main(args)

    subcommand = subparsers.add_parser(command_name,
                                       help='say sentence.')
    subcommand.add_argument('-s',
                            '--sentence',
                            type=str,
                            default=None,
                            help='sentence',
                            required=False)
    subcommand.add_argument('-e',
                            '--engine',
                            type=str,
                            default='mpg123',
                            help='mp3 engine, default mpg123',
                            required=False)
    subcommand.add_argument('-l',
                            '--lang',
                            type=str,
                            default='en',
                            help='IETF language tag, example: en, ja, zh-CN, zh-TW',
                            required=False)
    subcommand.add_argument('-t',
                            '--tmpdir',
                            type=str,
                            default=os.path.join(tempfile.gettempdir(), 'tts'),
                            help='temp directory',
                            required=False)
    subcommand.set_defaults(handler=handler)
