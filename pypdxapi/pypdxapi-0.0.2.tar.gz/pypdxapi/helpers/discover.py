""" Python implementation of Paradox module discover."""
import sys
import logging
from socket import (socket, timeout, AF_INET, SOCK_DGRAM, IPPROTO_UDP, SOL_SOCKET, SO_REUSEADDR,
                    SO_REUSEPORT, SO_BROADCAST)
from urllib.parse import parse_qsl
from time import sleep
from typing import List


_LOGGER = logging.getLogger(__name__)


def discover_modules(num_attempts: int = 5) -> List[dict]:
    port = 10000

    discovery = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    set_sock_opt(discovery, SO_REUSEADDR, 1)
    set_sock_opt(discovery, SO_REUSEPORT, 1)
    set_sock_opt(discovery, SO_BROADCAST, 1)
    discovery.settimeout(0.2)

    modules = []
    try:
        discovery.bind(('', port))
        for _ in range(num_attempts):
            _LOGGER.debug(f"Sent Paradox discover service announcement...")
            discovery.sendto(b'paradoxip?', ('<broadcast>', port))
            sleep(0.5)

            while True:
                try:
                    data, addr = discovery.recvfrom(1024)
                except timeout:
                    break
                else:
                    response = data.decode()
                    if response.startswith('paradoxip!'):
                        _LOGGER.debug(f"Found Paradox module on {addr}: {response}")
                        modules.append(parse_response(response))

    except OSError as err:
        _LOGGER.error(f"Discovery error: {err}")
    finally:
        discovery.close()

    return parse_modules(modules)


def set_sock_opt(sck: socket, optname: int, value: int):
    try:
        sck.setsockopt(SOL_SOCKET, optname, value)
    except AttributeError:
        _LOGGER.error(f"Systems don't support this socket option {optname} with value: {value}")
        pass


def parse_response(result: str) -> dict:
    if sys.version_info >= (3, 9):
        return dict(parse_qsl(result.removeprefix('paradoxip!')))

    return dict(parse_qsl(result[len('paradoxip!'):]))


def parse_modules(modules: List[dict]) -> List[dict]:
    return [dict(t) for t in {tuple(d.items()) for d in modules}]
