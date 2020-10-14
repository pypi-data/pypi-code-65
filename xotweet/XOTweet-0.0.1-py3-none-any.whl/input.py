# !/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser, Namespace, ArgumentTypeError
from datetime import datetime
from typing import Tuple, List


def strtobool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')


def strToList(v):
    items = v.split(",")
    if len(items) >= 1:
        return items
    else:
        raise ArgumentTypeError('Expected list')


def strToDateTime(v):
    return datetime.strptime(v, '%Y-%m-%d').date()


def parse_args() -> Tuple[Namespace, List[str]]:
    """ Parses the args from command line
    Returns:
        Tuple[Namespace, List[str]]: Returns known parsed
        arguments and a list of unknown args
    """
    parser = ArgumentParser()

    parser.add_argument(
        "Keyword",
        metavar='Keyword',
        type=str,
        help="Give keyword to fetch results")

    parser.add_argument(
        "-f",
        dest="Format",
        required=False,
        default="json",
        help="Output format")

    parser.add_argument(
        "-x",
        dest="Exclude",
        required=False,
        default=[],
        type=strToList,
        nargs='?',
        help="exclude re-tweets and replies")

    parser.add_argument(
        "-d",
        dest="From_Date",
        required=False,
        default=None,
        type=strToDateTime,
        nargs='?',
        help="date to show tweets from")

    parser.add_argument(
        "-t",
        dest="Threads",
        required=False,
        default=5,
        type=int,
        help="Number of threads")

    args, unknown = parser.parse_known_args()

    return args, unknown
