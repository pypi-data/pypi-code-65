import tldextract
import validators

import sys
import argparse
from typing import Any, Iterator, Optional
import logging

logger = logging.Logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "domain",
        help="domain or file with domains to process. "
        "If none then stdin will be use",
        nargs="*",
    )

    parser.add_argument(
        "-d", "--depth",
        type=int,
        default=1,
        help="Depth of retrieved subdomains. 1 returns the root domain."
        " Default = 1"
    )

    parser.add_argument(
        "-D", "--max-depth",
        type=int,
        default=1,
        help="Max depth of retrieved subdomains. Default = 1"
    )

    parser.add_argument(
        "-u", "--unique",
        action="store_true",
        help="Avoid retrieving duplicate domains"
    )

    args = parser.parse_args()

    if args.depth < 1:
        args.depth = 1

    if args.depth > args.max_depth:
        args.max_depth = args.depth

    return args


def main():
    args = parse_args()
    try:
        retrieved_domains = {}
        for domain in read_text_targets(args.domain):
            for root_domain in get_root_domains(
                    domain,
                    min_depth=args.depth-1,
                    max_depth=args.max_depth-1
            ):
                if args.unique and root_domain in retrieved_domains:
                    continue

                print(root_domain)
                retrieved_domains[root_domain] = True

    except KeyboardInterrupt:
        pass


def get_root_domains(domain, min_depth=0, max_depth=0):
    domains_tree = []
    domain_parts = tldextract.extract(domain)
    root_domain = "{}.{}".format(domain_parts.domain, domain_parts.suffix)
    subdomains = domain_parts.subdomain.split(".") if domain_parts.subdomain else []

    depth = min_depth
    if depth == 0:
        domains_tree.append(root_domain)
        depth += 1

    for depth in range(depth, max_depth+1):
        if depth > len(subdomains):
            break
        subs = ".".join(subdomains[-depth:])
        domains_tree.append("{}.{}".format(subs, root_domain))

    return domains_tree


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

        if validators.domain(line) is not True:
            logger.warn("Invalid domain {}".format(line))
            continue

        yield line
