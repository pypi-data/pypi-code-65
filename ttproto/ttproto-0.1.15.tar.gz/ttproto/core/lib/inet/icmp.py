#!/usr/bin/env python3
#
#   (c) 2012  Universite de Rennes 1
#
# Contact address: <t3devkit@irisa.fr>
#
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


from ttproto.core.data import *
from ttproto.core.typecheck import *
from ttproto.core.lib.inet.meta import *
from ttproto.core.lib.inet.basics import *
from ttproto.core.lib.inet.ipv4 import *
from ttproto.core import exceptions

import ttproto.core.lib.inet.ipv4

__all__ = [
    'ICMP',
    'ICMPEchoRequest',
    'ICMPEchoReply',
    'ICMPEReq',
    'ICMPERep',
]


class _ICMPOptLengthDescription:
    def __getitem__(self, item):
        return "%d bytes" % (item * 8)


"""
Echo or Echo Reply Message [rfc792]

Echo or Echo Reply Message

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Type      |     Code      |          Checksum             |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |           Identifier          |        Sequence Number        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Data ...
   +-+-+-+-+-

"""


class ICMP(
    metaclass=InetPacketClass,
    fields=[
        ("Type", "type", UInt8, InetVariant()),
        ("Code", "code", UInt8, 0),
        ("Checksum", "chk", Hex(UInt16), 0), #InetIPv4Checksum()),
        ("Payload", "pl", Value)
    ],
    descriptions={
        "Type": {
            # source: http://www.iana.org/assignments/icmpv6-parameters
            "0": "Echo Reply",
            "1": "Unassigned",
            "2": "Unassigned",
            "3": "Destination Unreachable",
            "4": "Source Quench (Deprecated)",
            "5": "Redirect",
            "6": "Alternate Host Address (Deprecated)",
            "7": "Unassigned",
            "8": "Echo",
            "9": "Router Advertisement",
            "10": "Router Selection",
            "11": "Time Exceeded",
            "12": "Parameter Problem",
            "13": "Timestamp",
            "14": "Timestamp Reply",
            "15": "Information Request (Deprecated)",
            "16": "Information Reply (Deprecated)",
            "17": "Address Mask Request (Deprecated)",
            "18": "Address Mask Reply (Deprecated)",
            "19": "Reserved (for Security)",
            "30": "Traceroute (Deprecated)",
            "31": "Datagram Conversion Error (Deprecated)",
            "32": "Mobile Host Redirect (Deprecated)",
            "33": "IPv6 Where-Are-You (Deprecated)",
            "34": "IPv6 I-Am-Here (Deprecated)",
            "35": "Mobile Registration Request (Deprecated)",
            "36": "Mobile Registration Reply (Deprecated)",
            "37": "Domain Name Request (Deprecated)",
            "38": "Domain Name Reply (Deprecated)",
            "39": "SKIP (Deprecated)",
            "40": "Photuris",
            "41": "ICMP messages utilized by experimental mobility protocols such as Seamoby",
            "42": "Extended Echo Request",
            "43": "Extended Echo Reply",
            "253": "RFC3692-style Experiment 1",
            "254": "RFC3692-style Experiment 2",

        },
    }):
    @typecheck
    def find_type(self: is_flat_value, type_: is_type) -> optional(Value):
        result = super().find_type(type_)
        if result is not None:
            return result

        # try in the option list
        try:
            options = self["Options"]
        except exceptions.UnknownField:
            return None

        return None if options is None else options.find_type(type_)


class ICMPEcho(
    metaclass=InetPacketClass,
    variant_of=ICMP,
    prune=-1,
    fields=[
        ("Identifier", "id", Hex(UInt16), 0),
        ("SequenceNumber", "seq", UInt16, 0),
        ("Payload", "pl", bytes , b''),
    ]):
    pass


class ICMPEchoRequest(
    metaclass=InetPacketClass,
    variant_of=ICMPEcho,
    id=8, ): pass


class ICMPEchoReply(
    metaclass=InetPacketClass,
    variant_of=ICMPEcho,
    id=0, ): pass



# Aliases
ICMPEReq = ICMPEchoRequest
ICMPERep = ICMPEchoReply

# tell the ipv4 module that protocol 01 should be mapped to the ICMP class
ttproto.core.lib.inet.ipv4.ip_next_header_bidict.update({
    1: ICMP,
})
