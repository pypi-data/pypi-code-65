"""
Module that communicates with the OVSDB server
"""
import socket
import json
from datetime import datetime, timedelta
from typing import Dict

from ovsdbmanager import OvsdbQuery

TIMEOUT = 5
BUFSIZE = 1024


class OvsdbRpc:
    """
    OvsdbRpc
    """
    def __init__(self, ovsdb_ip: str, ovsdb_port: int, query: OvsdbQuery):
        self._ovsdb_ip = ovsdb_ip
        self._ovsdb_port = ovsdb_port
        self._query_timeout = TIMEOUT
        self.query = query

    def send(self, query: Dict):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.)
        s.connect((self._ovsdb_ip, self._ovsdb_port))
        s.send(json.dumps(query).encode())

        buf = bytes()
        bufsize = BUFSIZE

        timeout = datetime.now() + timedelta(seconds=self._query_timeout)

        while datetime.now() < timeout:
            buf += s.recv(bufsize)
            try:
                query_response = json.loads(buf.decode())

                if "method" in query_response.keys() and query_response["method"] == "echo":
                    echo_reply = self.query.echo_reply(query_response["params"],
                                                       query_response["id"])
                    s.send(json.loads(echo_reply).encode())
                    buf = bytes()
                else:
                    s.close()
                    return query_response

            except json.JSONDecodeError:
                pass
        raise TimeoutError("Connection timed out")
