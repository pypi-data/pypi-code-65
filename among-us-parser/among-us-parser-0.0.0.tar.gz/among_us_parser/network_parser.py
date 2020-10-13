import struct


class EthernetProtocol:

    def __init__(self, data: bytes):
        self.source = self.decode_mac_address(data[0:6])
        self.destination = self.decode_mac_address(data[6:12])
        self.ether_type = data[12:14].hex()
        self.data = data[14:]

    def __repr__(self):
        return f"<EthernetProtocol source : {self.source} destination : {self.destination} ether_type: {self.ether_type} data : {self.data.hex()}>"

    @staticmethod
    def decode_mac_address(data: bytes) -> str:
        raw_address = struct.unpack("!cccccc", data)
        return f"{raw_address[0].hex()}:{raw_address[1].hex()}:{raw_address[2].hex()}:{raw_address[3].hex()}:{raw_address[4].hex()}:{raw_address[5].hex()}"


class InternetProtocol:

    def __init__(self, et: EthernetProtocol):
        self.ethernet_protocol = et
        data = et.data
        self.version_and_header_length = data[0:1]
        self.differentiated_service_filed = data[1:2]
        self.total_length = struct.unpack("!H", data[2:4])[0]
        self.identification = data[4:6]
        self.flags_and_fragment_offset = data[6:8]
        self.time_to_live = data[8:9]
        self.protocol = data[9:10].hex()
        self.header_checksum = data[10:12]
        self.source_address = self.decode_address(data[12:16])
        self.destination_address = self.decode_address(data[16:20])
        self.data = data[20:]


    @staticmethod
    def decode_address(data):
        raw_address = struct.unpack("!cccc", data)
        part_1 = int.from_bytes(raw_address[0], "little", signed=False)
        part_2 = int.from_bytes(raw_address[1], "little", signed=False)
        part_3 = int.from_bytes(raw_address[2], "little", signed=False)
        part_4 = int.from_bytes(raw_address[3], "little", signed=False)
        return f"{part_1}.{part_2}.{part_3}.{part_4}"

    def __repr__(self):
        return f"<InternetProtocol version_and_header_length : {self.version_and_header_length.hex()} total_length : {self.total_length} protocol : {self.protocol} source: {self.source_address} destination : {self.destination_address} data : {self.data.hex()}>"


class UserDatagramProtocol:

    def __init__(self, ip: InternetProtocol):
        self.internet_protocol = ip
        data = ip.data
        self.source_port = struct.unpack("!H", data[0:2])[0]
        self.destination_port = struct.unpack("!H", data[2:4])[0]
        self.total_length = struct.unpack("!H", data[4:6])[0]
        self.checksum = data[6:8]
        self.data = data[8:]


    def __repr__(self):
        return f"<UserDatagramProtocol source-port : {self.source_port} destination-port : {self.destination_port} total_length : {self.total_length} data : {self.data.hex()}>"
