#!/usr/bin/env python3
"""
Author: Marcel van den Brink <marcel.vandenbrink@gmail.com>
Purpose: Say hello
"""

import argparse
import sys


def get_args(args):
    """Get the command-line arguments"""
    parser = argparse.ArgumentParser(description='Say hello')
    parser.add_argument('-n', '--name', metavar='name', default="world", help='name to greet')
    return parser.parse_args(args)


def get_greeting(arguments):
    """Get the string that can be used to print on screen"""
    args = get_args(arguments)
    return 'hello ' + args.name


def main():
    print(get_greeting(sys.argv[1:]))


if __name__ == '__main__':
    main()
