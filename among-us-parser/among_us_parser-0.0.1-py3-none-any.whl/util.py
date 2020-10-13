from pcapng import FileScanner
from pcapng.blocks import EnhancedPacket
from .network_parser import EthernetProtocol, InternetProtocol, UserDatagramProtocol
from .packets.base_packet import BasePacket
import datetime

def filter_for_packet_types(packets, types):
    for p in packets:
        if p.__class__ in types:
            yield p


def load_among_us_packets(path: str):
    file = open(path, mode="rb")
    packets = []
    scanner = FileScanner(file)
    for block in scanner:
        if type(block) == EnhancedPacket:
            payload = block.packet_payload_info
            timestamp = datetime.datetime.utcfromtimestamp(block.timestamp)
            ep = EthernetProtocol(payload[2])
            if ep.ether_type == "0800":  # check for ip
                ip = InternetProtocol(ep)
                if ip.protocol == "11":  # check for udp
                    udp = UserDatagramProtocol(ip)
                    if BasePacket.check_if_among_us_packet(udp):
                        among_us_packet = BasePacket(udp, timestamp)
                        packets.append(among_us_packet)
    return packets