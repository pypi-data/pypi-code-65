import json
import unittest
from pprint import pprint

from ttproto.core.lib import *
from ttproto.core.dissector import *


class TestTCP(unittest.TestCase):

    def setUp(self):
        # cap = Capture('tests/test_dumps/others/TCP_1.pcap')
        self.cap = Capture('tests/test_dumps/others/TCP_stream.pcap')

    def test_capture(self):
        f = self.cap.frames[0]

        if f.error:
            print(f.error)

        print(f.summary())

    def test_generate_packet(self):
        # let's try to generate a simple TCP packet.

        # note same syntax as scapy
        packet = HTTP()
        print(packet.display())
