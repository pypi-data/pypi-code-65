#!/usr/bin/env python3
from urllib.parse import urlparse

import argparse
import sys
import logging
from typing import Any, Iterator, Optional

from .challenge_parser import parse_challenge, TARGET_INFO_NAMES
from .requester import request_http, request_SMBv1, request_SMBv23

from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread
import json

logger = logging.getLogger(__name__)

DONE = -1


def parse_args():
    parser = argparse.ArgumentParser(
      description='Fetch and parse NTLM challenge messages from HTTP and SMB'
      ' services'
    )
    parser.add_argument(
        'target',
        help='HTTP or SMB URL to fetch NTLM challenge from',
        nargs="*",
    )
    parser.add_argument(
        '-1', '--smbv1',
        action='store_true',
        help='Use SMBv1 (for SMB requests)'
    )

    parser.add_argument(
        "-v", "--verbose",
        action="count",
        help="Verbosity",
        default=0
    )
    parser.add_argument(
        "-w", "--workers",
        help="Set the number of workers",
        default=10,
        type=int
    )

    parser.add_argument(
        "-j", "--json",
        metavar="FILE",
        help="Write json results in given file",
        type=argparse.FileType('w'),
    )

    return parser.parse_args()


def main():
    args = parse_args()
    init_log(args.verbose)

    pool = ThreadPoolExecutor(args.workers)
    q = Queue()
    t_print = launch_printer(q, args.json)

    for url in read_text_targets(args.target):
        pool.submit(work, q, url, args.smbv1)

    pool.shutdown(wait=True)
    q.put(DONE)
    t_print.join()


def init_log(verbosity=0, log_file=None):

    if verbosity == 1:
        level = logging.WARN
    elif verbosity == 2:
        level = logging.INFO
    elif verbosity > 2:
        level = logging.DEBUG
    else:
        level = logging.CRITICAL

    logging.basicConfig(
        level=level,
        filename=log_file,
        format="%(levelname)s:%(name)s:%(message)s"
    )


def work(queue, url, smbv1=False):
    try:
        challenge = request_ntlm_challenge(url, smbv1=smbv1)
        queue.put((url, challenge))
    except Exception as ex:
        logger.warning("Error with '{}': {}".format(url, ex))


def launch_printer(q: Queue, json_file=None):
    results_iter = queue_to_iter(q)
    t_print = Thread(
        target=process_challenges,
        args=(
            results_iter,
        ),
        kwargs={
            "json_file": json_file
        }
    )
    t_print.start()
    return t_print


def queue_to_iter(q: Queue):
    """Allows to process the consumption of the queue as an iterator
    """
    while True:
        value = q.get()
        if value == DONE:
            return
        yield value


def process_challenges(challenges, json_file=None):

    results = []

    for url, challenge in challenges:
        try:
            parsed_challenge = parse_challenge(challenge)
            print_challenge(url, parsed_challenge)
            results.append((url, parsed_challenge))
        except Exception:
            logger.exception("Error parsing challenge of %s", url)

    if json_file and results:
        save_json_results(json_file, results)


DEFAULT_PORTS = {
    "smb": 445,
    "http": 80,
    "https": 443
}


def save_json_results(json_file, results):
    json_array = []
    for url, challenge in results:
        url_p = urlparse(url)

        port = url_p.port
        if port is None:
            port = DEFAULT_PORTS[url_p.scheme]

        json_array.append({
            "target": {
                "url": url,
                "protocol": url_p.scheme,
                "host": url_p.hostname,
                "port": port
            },
            "challenge": {
                "target_name": challenge.target_name,
                "os": {
                    "major_version": challenge.version.major,
                    "minor_version": challenge.version.minor,
                    "build": challenge.version.build,
                    "names": challenge.version.names,
                },
                "target_info": challenge.target_info,
                "negotiate_flags": {
                    "value": challenge.negotiate_flags,
                    "names": challenge.negotiate_flags_names
                },
                "server_challenge": challenge.server_challenge
            }
        })

    logger.info("Results saved in {}".format(json_file.name))
    json.dump(json_array, json_file)


def print_challenge(url, challenge):
    msg = []
    msg.append("\nUrl: {}".format(url))
    if 'NTLMSSP_TARGET_TYPE_DOMAIN' in challenge.negotiate_flags_names:
        msg.append('Target (Domain): {}'.format(challenge.target_name))
    elif 'NTLMSSP_TARGET_TYPE_SERVER' in challenge.negotiate_flags_names:
        msg.append('Target (Server): {}'.format(challenge.target_name))

    version = challenge.version
    msg.append("OS Version: {}.{}.{}".format(
        version.major, version.minor, version.build
    ))
    msg.append("OS Name: {}".format(" | ".join(version.names)))

    target_info = challenge.target_info
    for name in TARGET_INFO_NAMES:
        try:
            msg.append("{}: {}".format(name, target_info[name]))
        except KeyError:
            pass

    msg.append('Negotiate Flags: {}'.format(hex(challenge.negotiate_flags)))
    for name in challenge.negotiate_flags_names:
        msg.append("  {}".format(name))

    msg.append("Server challenge: {}".format(challenge.server_challenge))

    print("\n".join(msg), flush=True)


def request_ntlm_challenge(url, smbv1=False):
    url_p = urlparse(url)

    if url_p.scheme == 'smb':
        host = url_p.hostname
        port = url_p.port or 445

        if smbv1:
            return request_SMBv1(host, port)
        else:
            return request_SMBv23(host, port)

    elif url_p.scheme.startswith('http'):
        return request_http(url)

    raise Exception('Invalid URL, expecting http[s]://... or smb://...'.format(url))


def get_default_port(protocol):
    return {
        "smb": 445,
        "http": 80,
        "https": 443
    }[protocol]


def read_text_targets(targets: Any) -> Iterator[str]:
    yield from read_text_lines(read_targets(targets))


def read_targets(targets: Optional[Any]) -> Iterator[str]:
    """Function to process the program ouput that allows to read an array
    of strings or lines of a file in a standard way. In case nothing is
    provided, input will be taken from stdin.
    """
    if not targets:
        yield from sys.stdin

    for target in targets:
        try:
            with open(target) as fi:
                yield from fi
        except FileNotFoundError:
            yield target


def read_text_lines(fd: Iterator[str]) -> Iterator[str]:
    """To read lines from a file and skip empty lines or those commented
    (starting by #)
    """
    for line in fd:
        line = line.strip()
        if line == "":
            continue
        if line.startswith("#"):
            continue

        yield line


if __name__ == '__main__':
    main()
