import argparse
import dns.resolver
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from functools import partial
import sys
from ipaddress import ip_address
import logging

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "names",
        nargs="*",
        help="Specify several domain or files. If None then stdin is used"
    )

    parser.add_argument(
        "--workers",
        "-w",
        default=10,
        type=int,
        help="Number of concurrent workers"
    )

    parser.add_argument(
        "--tcp",
        action="store_true",
        default=False,
        help="Use TCP"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=5000,
        help="Timeout milliseconds, default 5000"
    )

    parser.add_argument(
        "--nameservers",
        nargs="+",
        help="Custom name servers"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        help="Verbosity",
        default=0
    )

    parser.add_argument(
        "-I", "--no-ip",
        help="Do not show ips",
        action="store_true"
    )

    parser.add_argument(
        "-D", "--no-domain",
        help="Do not show domains",
        action="store_true"
    )

    args = parser.parse_args()
    args.timeout = args.timeout / 1000

    return args


def main():
    args = parse_args()
    init_log(args.verbose)

    pool = ThreadPoolExecutor(args.workers)
    print_lock = Lock()

    resolver = dns.resolver.Resolver()
    resolver.timeout = args.timeout

    if args.nameservers:
        resolver.nameservers = args.nameservers

    logger.info("Nameservers: %s", ", ".join(resolver.nameservers))

    partial_resolve_domain = partial(
        resolve_domain,
        resolver=resolver,
        tcp=args.tcp
    )

    partial_resolve_ip = partial(
        resolve_ip,
        resolver=resolver,
        tcp=args.tcp
    )

    partial_print_names = partial(
        print_names,
        show_ips=not args.no_ip,
        show_domains=not args.no_domain
    )

    for hostname in read_input(args.names):
        pool.submit(
            dns_resolution,
            partial_resolve_domain,
            partial_resolve_ip,
            hostname,
            print_lock,
            partial_print_names,
            args.verbose
        )


def is_ip(host):
    try:
        ip_address(host)
        return True
    except ValueError:
        return False


def resolve_ip(ip, resolver, tcp):
    logger.info("Resolving ip %s", ip)
    domains = resolver.resolve(ip, 'PTR', tcp=tcp)
    print(domains)
    return [str(d) for d in domains]


def resolve_domain(domain, resolver, tcp):
    logger.info("Resolving domain %s", domain)
    ips = resolver.resolve(domain, 'A', tcp=tcp)
    return [str(ip) for ip in ips]


def dns_resolution(
        resolve_domain,
        resolve_ip,
        host,
        print_lock,
        print_names,
        verbose
):
    try:
        if is_ip(host):
            hostnames = resolve_ip(host)
            ips = [host]
        else:
            ips = resolve_domain(host)
            hostnames = [host]
    except Exception as ex:
        logger.warning("Error '%s': %s", host, ex)
        raise ex

    with print_lock:
        print_names(hostnames, ips)


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


def read_input(names):
    if not names:
        for name in read_text_lines(sys.stdin):
            yield name
        return

    for name in names:
        try:
            with open(name) as fi:
                for line in read_text_lines(fi):
                    yield line
        except FileNotFoundError:
            # name must be a domain name
            yield name


def read_text_lines(fd):
    for line in fd:
        line = line.strip()
        if line == "" or line.startswith("#"):
            continue

        yield line


def print_names(domains, ips, show_ips=True, show_domains=True):
    groups = []

    if show_domains:
        groups.append(",".join(domains))

    if show_ips:
        groups.append(",".join(ips))

    print(" ".join(groups), flush=True)
