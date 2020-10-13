from .command import Command
from .connection import Connection
from .client_base import ClientBase

from amcp_pylib.response import (
    Base as ResponseBase,
    Factory as ResponseFactory,
)


class Client(ClientBase):
    """ Connection client class. """
    
    def connect(self, host: str = "127.0.0.1", port: int = 5250):
        """ Initialize TCP connection to given host address and port. """
        if not self.connection:
            self.connection = Connection(host, port)

    def send(self, command: Command) -> ResponseBase:
        """ Convert command to bytes and then send it via established server connection. """
        return self.send_raw(bytes(command))

    def send_raw(self, data: bytes) -> ResponseBase:
        """ Send bytes via established server connection. """
        self.connection.send(data)
        return self.process_response()

    def process_response(self) -> ResponseBase:
        """ Receive data from server, parse it and create corresponding class. """
        data = self.connection.receive()
        return ResponseFactory.create_from_bytes(data)
