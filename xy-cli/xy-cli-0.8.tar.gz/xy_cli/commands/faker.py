#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ..libs.XlsxLoader import XlsxLoader
from ..libs.DataFactory import DataFactory
from ..libs.util import json_serial

import sys, os, json
import pprint
import argparse

command_name = os.path.basename(__file__).split('.', 1)[0].replace("_", ":")


def main(args):

    data = XlsxLoader().load_data(args.file,
                                  args.sheet,
                                  header_row=args.header_row,
                                  header_col=args.header_col,
                                  end_row=args.end_row,
                                  end_col=args.end_col)

    if args.debug:
        print("filter_title: %s" % args.filter_title)
        print("filter: %s" % args.filter)
        print("header: %s" % ",".join(data[0].keys()))
        print("first-row: %s" % ",".join(data[1].values()))

    if args.filter and args.filter_title:
        data = [row for row in data if row[args.filter_title] in args.filter]

    if data is None or len(data) == 0:
        print("no data!")
        return

    dataFactory = DataFactory(args.langs)
    result = []
    limit_size = args.limit
    for size in range(0, limit_size):
        item = {}
        for row in data:
            if row["mock_type"] or row.get("mock_default_value"):
                item[row["mock_key"]] = dataFactory.get_mock_data(
                    row["mock_type"], row.get("mock_default_value"), (size + 1))
        result.append(item)

    header = result[0].keys()
    table_name = args.sheet
    if args.type == 'json':
        print(json.dumps(result, default=json_serial, indent=2, sort_keys=False, ensure_ascii=False))
    elif args.type == 'csv':
        print(",".join(header))
        for row in result:
            print(",".join(row.values()))
    elif args.type == 'sql':
        columns = " , ".join(header)
        for row in result:
            values = [
                "'%s'" % ",".join(v) if type(v) is list else "'%s'" % str(v)
                for v in row.values()
            ]
            sql = "INSERT INTO {TABLE_NAME} ({COLUMNS}) VALUES ({VALUES});".format(
                TABLE_NAME=table_name,
                COLUMNS=columns, VALUES=" , ".join(values))
            print(sql)
    elif args.type == 'code':
        for idx, row in enumerate(result):
            for key, value in row.items():
                print("%s%s.%s = '%s';" % (table_name, idx, key, value))
            print()

def register(parser, subparsers, **kwargs):

    def handler(args):
        if args.file is None:
            print(parser.parse_args([command_name, '--help']))
            return
        if args.file:
            main(args)

    subcommand = subparsers.add_parser(command_name,
                                       help='create faker json data. ')
    subcommand.add_argument('-f',
                            '--file',
                            type=str,
                            default=None,
                            help='xlsx file',
                            required=False)
    subcommand.add_argument('-s',
                            '--sheet',
                            type=str,
                            help='sheet name',
                            required=False)
    subcommand.add_argument('--header_row',
                            type=int,
                            default=0,
                            help='header_row, default 0',
                            required=False)
    subcommand.add_argument('--header_col',
                            type=int,
                            default=0,
                            help='header_col, default 0',
                            required=False)
    subcommand.add_argument('--end_row',
                            type=int,
                            default=None,
                            help='end_row',
                            required=False)
    subcommand.add_argument('--end_col',
                            type=int,
                            default=None,
                            help='end_col',
                            required=False)
    subcommand.add_argument('--filter',
                            nargs="*",
                            help='meta_type',
                            required=False)
    subcommand.add_argument('--filter_title',
                            type=str,
                            help='filter_title',
                            default='filter',
                            required=False)
    subcommand.add_argument('--debug',
                            action='store_true',
                            help='debug',
                            required=False)
    subcommand.add_argument(
        '-l',
        '--langs',
        nargs='*',
        default=['ja_JP'],
        help=
        "languages, default 'ja_JP'. example: 'en_US', 'ja_JP', 'zh_CN', 'zh_TW'",
        required=False)
    subcommand.add_argument('-m',
                            '--limit',
                            type=int,
                            default=5,
                            help='generate size, default 5',
                            required=False)
    subcommand.add_argument('-t',
                            '--type',
                            type=str,
                            default='json',
                            choices=['json', 'csv', 'sql', 'code'],
                            help='format type',
                            required=False)
    subcommand.set_defaults(handler=handler)
