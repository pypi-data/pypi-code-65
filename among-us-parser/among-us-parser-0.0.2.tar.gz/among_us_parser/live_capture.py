import socket
from among_us_parser.packets import BasePacket
from .network_parser import EthernetProtocol, InternetProtocol, UserDatagramProtocol
import datetime
from typing import List

class AmongUsPacketCapturer:

    def __init__(self, network_interface_ip: str):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW)
        self.socket.bind((network_interface_ip, 0))
        self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    def try_get_package(self) -> List[BasePacket]:
        bytes = self.socket.recvfrom(65535)[0]
        return self.parse_live_packet(bytes)

    def get_package(self) -> List[BasePacket]:
        among_us_packet = None
        while among_us_packet == None:
            bytes = self.socket.recvfrom(65535)[0]
            among_us_packet = self.parse_live_packet(bytes)
        return among_us_packet

    @staticmethod
    def parse_live_packet(packet: bytes) -> List[BasePacket]:
        # Workaround InternetProtocol needs a EthernetProtocol but the packet is already an ip package
        ep = EthernetProtocol(packet)
        ep.data = packet

        ip = InternetProtocol(ep)
        if ip.protocol == "11":  # check for udp
            udp = UserDatagramProtocol(ip)
            if BasePacket.check_if_among_us_packet(udp):
                return BasePacket.get_among_us_packets_from_udp(udp, datetime.datetime.now())

