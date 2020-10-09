import socket


class BaseConnection:
    PROTOCOL = {
        "TCP": socket.SOCK_STREAM,
        "UDP": socket.SOCK_DGRAM
    }
