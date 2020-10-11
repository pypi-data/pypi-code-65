#! /usr/bin/env python3


import argparse
import re

from . import constants
from . import streamchecker


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--version', help='show version', action='store_true')
    parser.add_argument(
        '-c', '--check-streams', help='check online streams and output names',
        action='store_true')
    parser.add_argument(
        '-l', '--check-links', help='check online streams and output links',
        action='store_true')
    parser.add_argument(
        '-d', '--check-displaynames', action='store_true',
        help='check online streams and output displaynames')
    parser.add_argument(
        '-p', '--play', action='store_true',
        help='check streams and choose one to play')
    args = parser.parse_args()
    return args


def checkOnline():
    streamers = streamchecker.Streamers()
    online = streamers.getStreaming()
    if online:
        for stream in online:
            yield stream


def play_twitch():
    streamers = streamchecker.StreamPlay('cli.json')
    streams = streamers.getStreaming()
    if not streams:
        return
    for i, stream in enumerate(streams):
        print(f'#{i+1} ' + stream.dispName())

    nro = input('(n/#) ')
    yes = re.compile(r'^[1-9][0-9]*$')
    no = re.compile(r'((n|N)(o|O)?|(c|C)((a|A)(n|N)(c|C)(e|E)(l|L))?)?')

    if no.fullmatch(nro):
        return
    try:
        match = yes.fullmatch(nro).group(0)
        if int(match) > len(streams):
            raise AttributeError()
    except AttributeError:
        print('Invalid input')
        return

    streamer = streams[int(match)-1]
    streamers.play(streamer)


def main():
    args = arg_parser()

    if args.version:
        print(f'{constants.__version__}')
        return
    elif args.check_streams:
        for stream in checkOnline():
            print(stream.name())
    elif args.check_displaynames:
        for stream in checkOnline():
            print(stream.dispName())
    elif args.check_links:
        for stream in checkOnline():
            print(stream.url())
    elif args.play:
        play_twitch()


if __name__ == '__main__':
    main()
