#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, argparse
from ..libs import slack

command_name = os.path.basename(__file__).split('.', 1)[0].replace("_", ":")


def register(parser, subparsers, **kwargs):

    def handler(args):
        if args.token is None or args.channel is None or args.msg is None:
            print(parser.parse_args([command_name, '--help']))
            return
        if args.file:
            res = slack.send_file(token=args.token,
                            channel=args.channel,
                            initial_comment=args.msg,
                            username=args.username,
                            filepath=args.file)
        else:
            res = slack.post_message(token=args.token,
                            channel=args.channel,
                            text=args.msg,
                            username=args.username,
                            icon_emoji=args.icon)
        print(res.text)

    subcommand = subparsers.add_parser(command_name, help='slack message.')
    subcommand.add_argument('-t',
                            '--token',
                            type=str,
                            help='token',
                            default=os.getenv('SLACK_BOT_TOKEN'),
                            required=False)
    subcommand.add_argument('-c',
                            '--channel',
                            type=str,
                            help='channel',
                            default='#general',
                            required=False)
    subcommand.add_argument('-m',
                            '--msg',
                            type=str,
                            help='message',
                            required=True)
    subcommand.add_argument('-f',
                            '--file',
                            type=str,
                            help='file',
                            required=False)
    subcommand.add_argument('-u',
                            '--username',
                            type=str,
                            help='username',
                            default='XySlackBot',
                            required=False)
    subcommand.add_argument('-i',
                            '--icon',
                            type=str,
                            help='icon',
                            default=':rabbit:',
                            required=False)
    subcommand.set_defaults(handler=handler)
