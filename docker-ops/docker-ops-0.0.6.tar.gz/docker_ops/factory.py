#!/usr/bin/env python

import argparse
import os
import typing

DESCRIPTION = """ Type `docker-ops.py` <command> -h for help."""
def obtain_options(args: typing.List[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
            description=DESCRIPTION,
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--source-paths', default='', type=str,
            help="When building Docker Images, sometimes we'll want to include source code directories.\n" +
            "Input a filepath relative to Dockerfile that'll scan for source to be included.\n" +
            "Values can be inserted in a CSV list format: one.py,two.cfg,three.etc")
    parser.add_argument('-d', '--directory', default=os.getcwd(), type=str,
            help='Which directory should docker_ops scan?')
    parser.add_argument('-b', '--build', default=True, action='store_false',
            help='Disable build, only request info?')
    parser.add_argument('-s', '--schedule', default=False, action='store_true',
            help='Schedule a service to be ran on a Cron Schedule')
    parser.add_argument('-c', '--cron-entry', type=str,
            help='m h dom mon dow command: docker pull ... && docker run -d ...')

    if args is None:
        options = parser.parse_args()

    else:
        options = parser.parse_args(args)

    options.source_paths = [item for item in options.source_paths.split(',') if item]
    return options

def main() -> None:
    options = obtain_options()
    if options.build:
        from docker_ops import scan
        scan.scan_and_build(options.directory, options.source_paths)

    elif options.schedule:
        options.source_paths = options.source_paths.split(',')
        from docker_ops import schedule
        schedule.crontab(options.cron_entry)

def run_from_cli() -> None:
    import sys, os
    sys.path.append(os.getcwd())
    main()

if __name__ == '__main__':
    main()
