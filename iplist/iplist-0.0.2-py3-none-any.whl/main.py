import argparse
from ipaddress import ip_network, ip_address, summarize_address_range
from typing import Any, Iterator, Optional
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Convert IP ranges")

    parser.add_argument(
        "range",
        help="Range in CIDR format (10.0.0.0/24) or"
        " start ip-end ip (10.0.0.0-10.0.0.255). Or file with ranges. "
        "If none stdin is used",
        nargs="*",
    )

    parser.add_argument(
        "-c", "--cidr",
        help="Convert IP ranges into CIDR representation and viceversa",
        action="store_true",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.cidr:
        convert_ips = convert_ranges
    else:
        convert_ips = list_ips

    for t in read_text_targets(args.range):
        try:
            for ip in convert_ips(t):
                print(ip)
        except ValueError:
            perror("%s is not a valid range" % t)


def list_ips(ip_range: str) -> Iterator[str]:
    try:
        ip_range = ip_network(ip_range)
        for ip in ip_range:
            yield str(ip)
    except ValueError:
        start_ip, end_ip = ip_range.split("-")

        start_ip = ip_address(start_ip)
        end_ip = ip_address(end_ip)

        while start_ip <= end_ip:
            yield str(start_ip)
            start_ip += 1


def convert_ranges(ip_range: str) -> Iterator[str]:
    try:
        ip_range = ip_network(ip_range)
        yield "{}-{}".format(ip_range[0], ip_range[-1])
    except ValueError:
        start_ip, end_ip = ip_range.split("-")

        start_ip = ip_address(start_ip)
        end_ip = ip_address(end_ip)

        for ip_range in summarize_address_range(start_ip, end_ip):
            yield str(ip_range)


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


def perror(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)
