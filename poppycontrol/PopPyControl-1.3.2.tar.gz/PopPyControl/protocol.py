from PopPyControl.packet import Packet
from time import sleep

# Variavel de tempo
delaytime = 0.002


def write(port, req):
    clearPort(port)
    sleep(delaytime)
    port.write(req)
    port.flush()


def read(port, req):
    res = b''
    trys = 0

    while True:
        test = port.read(size=1)
        if test != b'':
            res += test
        else:
            trys += 1

            if trys > 3:
                break

    sleep(delaytime)
    return Packet(req, res)


def pingCommand(port, id):
    req = b''
    res = ''

    if type(id) != int:
        sleep(delaytime)
        return Packet(req, res)

    checksum = int(255 - ((int(id) + 0x03) % 256))

    req += b'\xff'
    req += b'\xff'
    req += bytes([id])
    req += b'\x02'
    req += b'\x01'
    req += bytes([checksum])

    write(port, req)
    return read(port, req)


def readCommand(port, id, address, size):
    req = b''
    res = b''

    if type(id) != int or type(address) != int or type(size) != int:
        sleep(delaytime)
        return Packet(req, res)

    checksum = int(255 - ((int(id) + 0x06 + int(address) + int(size)) % 256))

    req += b'\xff'
    req += b'\xff'
    req += bytes([id])
    req += b'\x04'
    req += b'\x02'
    req += bytes([address])
    req += bytes([size])
    req += bytes([checksum])

    write(port, req)
    return read(port, req)


def writeCommand(port, id, address, size, value):
    req = b''
    res = b''

    if type(id) != int:
        sleep(delaytime)
        return Packet(req, res)
    elif type(address) != int:
        sleep(delaytime)
        return Packet(req, res)
    elif type(size) != int:
        sleep(delaytime)
        return Packet(req, res)
    elif type(value) != int:
        sleep(delaytime)
        return Packet(req, res)

    value1 = 0
    value2 = 0
    length = size + 3

    req += b'\xff'
    req += b'\xff'
    req += bytes([id])
    req += bytes([length])
    req += b'\x03'
    req += bytes([address])

    if size == 1:
        req += bytes([value])
        checksum = 255 - ((id + length + 3 + address + value) % 256)
    elif size == 2:
        value1 = value % 256
        value2 = int((value - (value % 256))/256)
        req += bytes([value1])
        req += bytes([value2])
        checksum = 255 - ((id + length + 3 + address + value1 + value2) % 256)

    req += bytes([checksum])

    write(port, req)
    return read(port, req)


def clearPort(serialPort):
    while True:
        trash = serialPort.read()
        if trash == b'':
            break
