import socket
from threading import Thread
from dan_socket.event import Event
from dan_socket.base import BaseConnection

class ClientConnection:
    def __init__(self, client_sock, server):
        self.client_sock = client_sock
        self.server = server
        self.handle_connection()

    def send(self, message):
        self.client_sock.send(message.encode())

    def read_loop(self):
        while True:
            message = self.client_sock.recv(1024)
            if len(message) == 0:
                break
            self.server.event.trigger_event("on_message", self, message)
        self.server.connection_closed(self)

    def handle_connection(self):
        Thread(target=ClientConnection.read_loop, args=(self, )).start()


class DanServer(BaseConnection):
    PROTOCOL = {
        "TCP": socket.SOCK_STREAM,
        "UDP": socket.SOCK_DGRAM
    }

    def __init__(self, host, port, protocol="TCP", max_connections=50):
        self._sock = socket.socket(socket.AF_INET, BaseConnection.PROTOCOL[protocol])
        self._sock.bind((host, port))
        self._clients = {}
        self.max_connections = max_connections
        self.event = Event  # it's a class not object

    def connection_closed(self, client):
        client.client_sock.close()
        if client in self._clients:
            del self._clients[client]
        self.event.trigger_event("on_connection_closed", client)

    def start(self):
        self._sock.listen(self.max_connections)
        while True:
            client_sock, address = self._sock.accept()
            client = ClientConnection(client_sock, self)
            self._clients[client] = address
            self.event.trigger_event("on_new_connection", client)
