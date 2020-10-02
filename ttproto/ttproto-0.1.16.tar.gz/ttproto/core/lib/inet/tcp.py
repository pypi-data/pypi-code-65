#!/usr/bin/env python3
# Author: Federico Sismondi
import logging

from ttproto.core.data import Value
from ttproto.core.packet import PacketValue, Optional
from ttproto.core.lib.inet.meta import *
from ttproto.core.lib.inet.basics import *
from contextlib import contextmanager

import ttproto.core.lib.inet.ipv6

__all__ = [
    "TCP",
    # "TCPSyn",
    # "TCPAck",
    # "TCPSynAck",
    # "TCPFin",
    # "TCPFinAck",

]

# map port_number -> type
tcp_port_map = {}

tcp_port_descriptions = {
    80: "http",
    5683: "coap",

}


# TCP Header Format (https://tools.ietf.org/html/rfc793#page-7)
#
#   0                   1                   2                   3
#   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |          Source Port          |       Destination Port        |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                        Sequence Number                        |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                    Acknowledgment Number                      |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |  Data |           |U|A|P|R|S|F|                               |
#  | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
#  |       |           |G|K|H|T|N|N|                               |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |           Checksum            |         Urgent Pointer        |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                    Options                    |    Padding    |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#  |                             data                              |
#  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

class _TCPSynTag(PacketValue.Tag):
    def post_decode(self, ctx, value):
        if value == 1:  # if syn then dont expect payload
            @contextmanager
            def decode_context():
                with ctx.replace_attr("expected_type", None):
                    yield

            # push context for Payload (field 16, starts counting from zero)
            ctx.push_context(16, decode_context())


class _TCPPort(PacketValue.Tag):
    def post_decode(self, ctx, value):
        expected_type = tcp_port_map.get(value)
        logging.debug("Expected type {}".format(expected_type))
        if expected_type:
            @contextmanager
            def decode_context():
                with ctx.replace_attr("expected_type", expected_type):
                    yield

            # push context for Payload (field 16, starts counting from zero)
            ctx.push_context(16, decode_context())


class _TCPHeaderLength(InetLength):
    def __init__(self):
        # TCP unit size = 4 * 8bits = 32 bits
        super().__init__("Options", 4)

    def post_decode(self, ctx, value):
        # len(TCP Header) - len(Option + Padding) = 5 (5 32bit words)

        super().post_decode(ctx, value - 5)


class TCP(
    metaclass=InetPacketClass,
    fields=[
        ("SourcePort", "sport", UInt16, _TCPPort()),
        ("DestinationPort", "dport", UInt16, _TCPPort()),
        ("SequenceNumber", "seq", UInt32, 0),
        ("AcknowledgmentNumber", "acknbr", UInt32, 0),
        ("DataOffset", "dataoffs", UInt4, _TCPHeaderLength()),
        ("ReservedField", "rf", Hex(UInt6), 0),
        ("Urg", "urg", bool, False),
        ("Ack", "ack", bool, False),
        ("Push", "psh", bool, False),
        ("Reset", "rst", bool, False),
        ("Syn", "syn", bool, _TCPSynTag()),
        ("Fin", "fin", bool, False),
        ("Window", "win", UInt16, 0),
        ("Checksum", "chk", Hex(UInt16), InetIPv6Checksum()),
        ("UrgentPointer", "urgptr", UInt16, 0),
        ("Options", "opt", bytes, b''),
        # ("Padding", "pad", bytes, b''),
        ("Payload", "pl", Optional(Value), b'')
    ],
    descriptions={
        "sport": tcp_port_descriptions,
        "dport": tcp_port_descriptions,
    }):

    def describe(self, desc):
        desc.src_port = self['sport']
        desc.dst_port = self['dport']

        flags = ''
        if self['syn']:
            flags += ' SYN'
        if self['ack']:
            flags += ' ACK'
        if self['urg']:
            flags += ' URG'
        if self['psh']:
            flags += ' PUSH'
        if self['rst']:
            flags += ' RST'
        if self['fin']:
            flags += ' FIN'

        if not self.describe_payload(desc):
            stxt = self.get_description("sport")
            dtxt = self.get_description("dport")
            desc.info = "TCP%s: %s -> %s" % (
                flags,
                stxt if stxt else str(self["sport"]),
                dtxt if dtxt else str(self["dport"]),
            )
        return True


# class TCPSyn(
#     metaclass=InetPacketClass,
#     variant_of=TCP,
#     prune=-1,
#     fields=[
#     ]):
#     pass


# tell the ip modules that ip next header 6 should be mapped to the TCP class
ttproto.core.lib.inet.ip.ip_next_header_bidict.update({6: TCP, })
