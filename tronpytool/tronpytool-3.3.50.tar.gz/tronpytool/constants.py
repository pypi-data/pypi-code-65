#!/usr/bin/env python
# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

# Here you can specify links to sites of different types.
# The default is verified links.
# If you do not know what links are used for, it is recommended not to change
from typing import Tuple

DEFAULT_NODES = {
    'full_node': 'https://api.trongrid.io',
    'solidity_node': 'https://api.trongrid.io',
    'event_server': 'https://api.trongrid.io'
}

CONF_MAINNET = {
    "full_node": "https://api.trongrid.io",
    "event_server": "https://api.trongrid.io",
}

# The long running, maintained by the tron-us community
CONF_SHASTA = {
    "full_node": "https://api.shasta.trongrid.io",
    "event_server": "https://api.shasta.trongrid.io",
    "faucet": "https://www.trongrid.io/faucet",
}

# Maintained by the official team
CONF_NILE = {
    "full_node": "https://httpapi.nileex.io",
    "event_server": "https://eventtest.nileex.io",
    "solidity_node": "https://httpapi.nileex.io",
    "faucet": "http://nileex.io/join/getJoinPage",
}

# Maintained by the official team
CONF_TRONEX = {
    "full_node": "https://testhttpapi.tronex.io",
    "event_server": "https://testapi.tronex.io",
    "faucet": "http://testnet.tronex.io/join/getJoinPage",
}

ALL = {
    "mainnet": CONF_MAINNET,
    "nile": CONF_NILE,
    "shasta": CONF_SHASTA,
    "tronex": CONF_TRONEX
}

RES_CODE = dict(
    SUCCESS=0,
    SIGERROR=1,
    CONTRACT_VALIDATE_ERROR=2,
    CONTRACT_EXE_ERROR=3,
    BANDWITH_ERROR=4,
    DUP_TRANSACTION_ERROR=5,
    TAPOS_ERROR=6,
    TOO_BIG_TRANSACTION_ERROR=7,
    TRANSACTION_EXPIRATION_ERROR=8,
    SERVER_BUSY=9,
    NO_CONNECTION=10,
    NOT_ENOUGH_EFFECTIVE_CONNECTION=11,
    OTHER_ERROR=20
)


def conf_for_name(name: str) -> dict:
    return ALL.get(name, None)


def handle_res(r: dict) -> Tuple[bool, str, str]:
    resultcode = r['result']['code']
    if RES_CODE.get(resultcode) > 0:
        return False, resultcode, r['result']['message']
    else:
        return True, resultcode, r['result']['message']
