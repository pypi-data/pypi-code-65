#!/usr/bin/env python3
#
#   (c) 2012  Universite de Rennes 1
#
# Contact address: <t3devkit@irisa.fr>
#
# See LICENSE file in root dir


"""
NOTES:
======


# Null Loopback cooked L2 generated in BSD systems

# check packet-null.c in wireshark for more info

# BSD AF_ values (family type values):
# BSD_AF_INET		2
# BSD_AF_ISO		7
# BSD_AF_APPLETALK	16
# BSD_AF_IPX		23
# BSD_AF_INET6_BSD	24	/* NetBSD, OpenBSD, BSD/OS */
# BSD_AF_INET6_FREEBSD	28	/* FreeBSD, DragonFly BSD */
# BSD_AF_INET6_DARWIN	30	/* OS X, iOS, anything else Darwin-based */

>>> ttproto.core.lib.encap.encap_type_bidict
BidictValueType(0, <class 'ttproto.core.lib.inet.basics.UInt32'>, {30: <class 'ttproto.core.lib.inet.ipv6.IPv6'>, 2: <class 'ttproto.core.lib.inet.ipv4.IPv4'>})

"""

import re

from ttproto.core.exceptions import Error
from ttproto.core.data import Value, BidictValueType
from ttproto.core.typecheck import *
from ttproto.core.lib.inet.meta import *
from ttproto.core.lib.inet.basics import *
from ttproto.core.lib.ports import socat
from ttproto.core.lib.ethernet import ethernet_type_bidict

__all__ = [
    'LinuxCookedCapture',
    'NullLoopback',
    'NullLoopbackBigEndian',
    # 'NullLoopbackLittleEndian',
]

encap_type_bidict = BidictValueType(0, UInt32)  # encap_type_bidict is populated by IPv4, IPv6, etc modules


class LinuxCookedCapture(
    metaclass=InetPacketClass,
    fields=[
        ("PacketType", "pty", UInt16),
        ("AddressType", "aty", UInt16),
        ("AddressLength", "aln", UInt16),
        ("Address", "adr", Bytes8),
        ("Protocol", "pro", UInt16, InetType(ethernet_type_bidict, "Payload")),
        # FIXME: values below 1537 are treated differently (see wireshark dissector packet-sll.c)
        ("Payload", "pl", Value),
    ],
    descriptions={
        "PacketType": {
            0: "unicast to us",
            1: "broadcast",
            2: "multicast",
            3: "unicast to another host",
            4: "sent by us",
        }
    }):
    def describe(self, desc):
        return self.describe_payload(desc)


class NullLoopback(
        metaclass=InetPacketClass,
        fields=[
            ("AddressFamily", "AF", UInt8, InetType(encap_type_bidict, "Payload")),
            ("ProtocolFamily", "PF", UInt24),
            ("Payload", "pl", Value),
        ],
        descriptions={
            "AddressFamily": {
                2: "BSD INET",
                7: "BSD ISO",
                16: "BSD APPLETALK",
                23: "BSD IPX",
                24: "BSD INET6 BSD",
                28: "BSD INET6 FREEBSD",
                30: "BSD INET6 DARWIN"
            }

        }):
    def describe(self, desc):
        return self.describe_payload(desc)


class NullLoopbackBigEndian(
        metaclass=InetPacketClass,
        fields=[
            ("ProtocolFamily", "PF", UInt24),
            ("AddressFamily", "AF", UInt8, InetType(encap_type_bidict, "Payload")),
            ("Payload", "pl", Value),
        ],
        descriptions={
            "AddressFamily": {
                2: "BSD INET",
                7: "BSD ISO",
                16: "BSD APPLETALK",
                23: "BSD IPX",
                24: "BSD INET6 BSD",
                28: "BSD INET6 FREEBSD",
                30: "BSD INET6 DARWIN"
            }

        }):
    def describe(self, desc):
        return self.describe_payload(desc)


# class NullLoopbackLittleEndian(
#     metaclass=InetPacketClass,
#     variant_of=NullLoopback,
#     prune=-3,
#     fields=[
#         ("AddressFamily", "AF", UInt8, InetType(encap_type_bidict, "Payload")),
#         ("ProtocolFamily", "PF", UInt24),
#         ("Payload", "pl", Value),
#     ],
# ):
#     pass

#
# __all__.extend(['NullLoopbackLittleEndian','NullLoopbackBigEndian',])

