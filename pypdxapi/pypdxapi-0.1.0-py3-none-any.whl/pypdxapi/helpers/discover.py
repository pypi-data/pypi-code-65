""" Python implementation of Paradox module discover."""
import sys
import logging
from typing import Optional, List
from socket import (socket, timeout, AF_INET, SOCK_DGRAM, IPPROTO_UDP, SOL_SOCKET, SO_REUSEADDR,
                    SO_REUSEPORT, SO_BROADCAST)
from urllib.parse import parse_qsl
from time import sleep

_LOGGER = logging.getLogger(__name__)


def discover_modules(num_attempts: int = 5) -> List[dict]:
    """ Discover paradox modules on the network.

    :param num_attempts: (optional) Number of discovery attempts.
    :return: List of discovered modules.
    """
    port = 10000

    discovery = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    _set_sock_opt(discovery, SO_REUSEADDR, 1)
    _set_sock_opt(discovery, SO_REUSEPORT, 1)
    _set_sock_opt(discovery, SO_BROADCAST, 1)
    discovery.settimeout(0.2)

    modules = []
    try:
        discovery.bind(('', port))
        for _ in range(num_attempts):
            _send_discover(discovery, port)

            response = _recv_discover(discovery)
            if response:
                modules.append(_parse_response(response))

    except OSError as err:
        _LOGGER.error("Discovery error: %s", err)
    finally:
        discovery.close()

    return _parse_modules(modules)


def _set_sock_opt(sck: socket, optname: int, value: int):
    try:
        sck.setsockopt(SOL_SOCKET, optname, value)
    except AttributeError:
        _LOGGER.error("Systems don't support this socket option %s with value: %s", optname, value)


def _send_discover(discovery: socket, port: int) -> None:
    _LOGGER.debug("Sent Paradox discover service announcement...")
    discovery.sendto(b'paradoxip?', ('<broadcast>', port))
    sleep(0.5)


def _recv_discover(discovery: socket) -> Optional[str]:
    while True:
        try:
            data, addr = discovery.recvfrom(1024)
        except timeout:
            break
        else:
            response = data.decode()
            if response.startswith('paradoxip!'):
                _LOGGER.debug("Found Paradox module on %s: %s", addr, response)
                return response

    return None


def _parse_response(result: str) -> dict:
    if sys.version_info >= (3, 9):
        return dict(parse_qsl(result.removeprefix('paradoxip!')))

    return dict(parse_qsl(result[len('paradoxip!'):]))


def _parse_modules(modules: List[dict]) -> List[dict]:
    return [dict(t) for t in {tuple(d.items()) for d in modules}]
