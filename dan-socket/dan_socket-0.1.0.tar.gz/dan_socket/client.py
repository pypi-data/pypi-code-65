import socket
from dan_socket.event import Event
from dan_socket.base import BaseConnection


class DanClient(BaseConnection):
    def __init__(self, host, port, protocol="TCP"):
        self._sock = socket.socket(socket.AF_INET, BaseConnection.PROTOCOL[protocol])
        self.host = host
        self.port = port
        self.event = Event  # it's a class not object

    def process_message(self, message):
        self.event.trigger_event("on_message", message)

    def connection_closed(self, client):
        client.client_sock.close()
        if client in self._clients:
            del self._clients[client]
        self.event.trigger_event("on_connection_closed", client)

    def start(self):
        self._sock.connect((self.host, self.port))
        while True:
            message = self._sock.recv(1024).decode()
            if len(message) == 0:
                break
            self.event.trigger_event("on_message", message)
        self.event.trigger_event("on_connection_closed")



