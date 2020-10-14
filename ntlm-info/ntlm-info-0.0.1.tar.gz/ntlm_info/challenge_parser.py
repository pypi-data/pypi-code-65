import datetime
from collections import OrderedDict
from typing import List, Optional, Dict

# parsing from "NT LAN Manager (NTLM) Authentication Protocol" v20190923, revision  31.0
# https://winprotocoldoc.blob.core.windows.net/productionwindowsarchives/MS-NLMP/%5bMS-NLMP%5d.pdf

TARGET_INFO_NAMES = [
    "MsvAvNbComputerName",
    "MsvAvNbDomainName",
    "MsvAvDnsComputerName",
    "MsvAvDnsDomainName",
    "MsvAvDnsTreeName",
    "MsvAvFlags",
    "MsvAvTimestamp",
    "MsvAvSingleHost",
    "MsvAvTargetName",
    "MsvAvChannelBindings"
]

NTLM_NEGOTIATE_FLAGS = OrderedDict()
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_UNICODE'] = 0x00000001
NTLM_NEGOTIATE_FLAGS['NTLM_NEGOTIATE_OEM'] = 0x00000002
NTLM_NEGOTIATE_FLAGS['NTLMSSP_REQUEST_TARGET'] = 0x00000004
NTLM_NEGOTIATE_FLAGS['UNUSED_10'] = 0x00000008
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_SIGN'] = 0x00000010
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_SEAL'] = 0x00000020
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_DATAGRAM'] = 0x00000040
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_LM_KEY'] = 0x00000080
NTLM_NEGOTIATE_FLAGS['UNUSED_9'] = 0x00000100
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_NTLM'] = 0x00000200
NTLM_NEGOTIATE_FLAGS['UNUSED_8'] = 0x00000400
NTLM_NEGOTIATE_FLAGS['NTLMSSP_ANONYMOUS'] = 0x00000800
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_OEM_DOMAIN_SUPPLIED'] = 0x00001000
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_OEM_WORKSTATION_SUPPLIED'] = 0x00002000
NTLM_NEGOTIATE_FLAGS['UNUSED_7'] = 0x00004000
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_ALWAYS_SIGN'] = 0x00008000
NTLM_NEGOTIATE_FLAGS['NTLMSSP_TARGET_TYPE_DOMAIN'] = 0x00010000
NTLM_NEGOTIATE_FLAGS['NTLMSSP_TARGET_TYPE_SERVER'] = 0x00020000
NTLM_NEGOTIATE_FLAGS['UNUSED_6'] = 0x00040000
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY'] = 0x00080000
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_IDENTIFY'] = 0x00100000
NTLM_NEGOTIATE_FLAGS['UNUSED_5'] = 0x00200000
NTLM_NEGOTIATE_FLAGS['NTLMSSP_REQUEST_NON_NT_SESSION_KEY'] = 0x00400000
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_TARGET_INFO'] = 0x00800000
NTLM_NEGOTIATE_FLAGS['UNUSED_4'] = 0x01000000
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_VERSION'] = 0x02000000
NTLM_NEGOTIATE_FLAGS['UNUSED_3'] = 0x10000000
NTLM_NEGOTIATE_FLAGS['UNUSED_2'] = 0x08000000
NTLM_NEGOTIATE_FLAGS['UNUSED_1'] = 0x04000000
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_128'] = 0x20000000
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_KEY_EXCH'] = 0x40000000
NTLM_NEGOTIATE_FLAGS['NTLMSSP_NEGOTIATE_56'] = 0x80000000


class OSVersion:

    def __init__(
            self,
            major: int, minor: int, build: int,
            names: Optional[List[str]] = None
    ):
        self.major = major
        self.minor = minor
        self.build = build
        self.names = names or []


class NtlmChallenge:

    def __init__(
            self,
            target_name: str,
            version: OSVersion,
            target_info: Dict[str, str],
            negotiate_flags: int,
            server_challenge: str
    ):
        self.target_name = target_name
        self.version = version
        self.target_info = target_info
        self.negotiate_flags = negotiate_flags
        self.server_challenge = server_challenge

    @property
    def negotiate_flags_names(self):
        names = []

        for name, value in NTLM_NEGOTIATE_FLAGS.items():
            if self.negotiate_flags & value:
                names.append(name)

        return names


def parse_challenge(challenge_message):

    # Signature
    # b'NTLMSSP\x00' --> NTLMSSP
    signature = decode_string(challenge_message[0:7])

    # MessageType
    # b'\x02\x00\x00\x00' --> 2
    message_type = decode_int(challenge_message[8:12])

    # TargetNameFields
    target_name_fields = challenge_message[12:20]
    target_name_len = decode_int(target_name_fields[0:2])
    target_name_max_len = decode_int(target_name_fields[2:4])
    target_name_offset = decode_int(target_name_fields[4:8])

    # NegotiateFlags
    negotiate_flags_int = decode_int(challenge_message[20:24])

    # negotiate_flags = parse_negotiate_flags(negotiate_flags_int)

    # ServerChallenge
    server_challenge = challenge_message[24:32]

    # Reserved
    reserved = challenge_message[32:40]

    # TargetInfoFields
    target_info_fields = challenge_message[40:48]
    target_info_len = decode_int(target_info_fields[0:2])
    target_info_max_len = decode_int(target_info_fields[2:4])
    target_info_offset = decode_int(target_info_fields[4:8])

    # Version
    version_bytes = challenge_message[48:56]
    version = parse_version(version_bytes)

    # TargetName
    target_name = challenge_message[target_name_offset:
                                    target_name_offset+target_name_len]
    target_name = decode_string(target_name)

    # TargetInfo
    target_info_bytes = challenge_message[target_info_offset:
                                          target_info_offset+target_info_len]

    target_info = parse_target_info(target_info_bytes)

    return NtlmChallenge(
        target_name,
        version,
        target_info,
        negotiate_flags_int,
        to_hex_string(server_challenge)
    )


def parse_negotiate_flags(negotiate_flags_int):
    negotiate_flags = []

    for name, value in NTLM_NEGOTIATE_FLAGS.items():
        if negotiate_flags_int & value:
            negotiate_flags.append(name)

    return negotiate_flags


def parse_version(version_bytes: bytes) -> OSVersion:

    major_version = version_bytes[0]
    minor_version = version_bytes[1]
    product_build = decode_int(version_bytes[2:4])

    names = []

    if major_version == 5 and minor_version == 1:
        names.append('Windows XP (SP2)')
    elif major_version == 5 and minor_version == 2:
        names.append('Server 2003')
    elif major_version == 6 and minor_version == 0:
        names.append("Server 2008")
        names.append("Windows Vista")
    elif major_version == 6 and minor_version == 1:
        names.append("Server 2008 R2")
        names.append("Windows 7")
    elif major_version == 6 and minor_version == 2:
        names.append("Server 2012")
        names.append("Windows 8")
    elif major_version == 6 and minor_version == 3:
        names.append("Server 2012 R2")
        names.append("Windows 8.1")
    elif major_version == 10 and minor_version == 0:
        names.append("Server 2016")
        names.append("Server 2019")
        names.append("Windows 10")

    return OSVersion(major_version, minor_version, product_build, names)


def parse_target_info(target_info_bytes):

    MsvAvEOL = 0x0000
    MsvAvNbComputerName = 0x0001
    MsvAvNbDomainName = 0x0002
    MsvAvDnsComputerName = 0x0003
    MsvAvDnsDomainName = 0x0004
    MsvAvDnsTreeName = 0x0005
    MsvAvFlags = 0x0006
    MsvAvTimestamp = 0x0007
    MsvAvSingleHost = 0x0008
    MsvAvTargetName = 0x0009
    MsvAvChannelBindings = 0x000A

    target_info = OrderedDict()
    info_offset = 0

    while info_offset < len(target_info_bytes):
        av_id = decode_int(target_info_bytes[info_offset:info_offset+2])
        av_len = decode_int(target_info_bytes[info_offset+2:info_offset+4])
        av_value = target_info_bytes[info_offset+4:info_offset+4+av_len]

        info_offset = info_offset + 4 + av_len

        if av_id == MsvAvEOL:
            pass
        elif av_id == MsvAvNbComputerName:
            target_info["MsvAvNbComputerName"] = decode_string(av_value)
        elif av_id == MsvAvNbDomainName:
            target_info["MsvAvNbDomainName"] = decode_string(av_value)
        elif av_id == MsvAvDnsComputerName:
            target_info["MsvAvDnsComputerName"] = decode_string(av_value)
        elif av_id == MsvAvDnsDomainName:
            target_info["MsvAvDnsDomainName"] = decode_string(av_value)
        elif av_id == MsvAvDnsTreeName:
            target_info["MsvAvDnsTreeName"] = decode_string(av_value)
        elif av_id == MsvAvFlags:
            pass
        elif av_id == MsvAvTimestamp:
            filetime = decode_int(av_value)
            microseconds = (filetime - 116444736000000000) / 10
            time = datetime.datetime(
                1970, 1, 1) + datetime.timedelta(microseconds=microseconds)
            target_info["MsvAvTimestamp"] = time.strftime(
                "%b %d, %Y %H:%M:%S.%f")
        elif av_id == MsvAvSingleHost:
            target_info["MsvAvSingleHost"] = decode_string(av_value)
        elif av_id == MsvAvTargetName:
            target_info["MsvAvTargetName"] = decode_string(av_value)
        elif av_id == MsvAvChannelBindings:
            target_info["MsvAvChannelBindings"] = to_hex_string(av_value)

    return target_info


def to_hex_string(byte_string):
    return ''.join('{:02x}'.format(x) for x in byte_string)


def decode_string(byte_string):
    return byte_string.decode('UTF-8').replace('\x00', '')


def decode_int(byte_string):
    return int.from_bytes(byte_string, 'little')
