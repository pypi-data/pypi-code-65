from alaya.packages.platon_keys.utils import bech32
from alaya.packages.eth_utils import to_checksum_address
from alaya.utils.encoding import tobech32address

MIANNETHRP = "atp"
TESTNETHRP = "atx"

def addresstoapt(arg: str):
    if isinstance(arg,str):
        if arg[:3] == 'lax':
            hrpgot, data1 = bech32.decode("lax", arg)
            if data1 is None:
                return False
            addr = to_checksum_address(bytes(data1))
            address = tobech32address(TESTNETHRP, addr)
        elif arg[:3] == 'lat':
            hrpgot, data1 = bech32.decode("lat", arg)
            if data1 is None:
                return False
            addr = to_checksum_address(bytes(data1))
            address = tobech32address(MIANNETHRP, addr)
        elif arg[:2] == '0x':
            address = tobech32address(MIANNETHRP, arg)
            if address is None:
                return False
        else:
            address=arg
    return address


