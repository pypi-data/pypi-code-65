import logging
import random
import socket

import sys
from clickhouse_driver import Client as CHClient, errors


class Client(CHClient):
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
    logging.captureWarnings(True)

    def __init__(self,
                 reconnect=False,
                 reconnect_attempts=10,
                 *args,
                 **kwargs):
        super(Client, self).__init__(*args, **kwargs)

        self.reconnect_attempts = reconnect_attempts or 1

        if reconnect:
            self.connection.force_connect = self.force_reconnect
        self.connection.connect = self.balanced_connect

    def force_reconnect(self):
        self.disconnect()
        if not self.connection.connected:
            self.connection.connect()

    def balanced_connect(self):
        conn = self.connection

        if conn.connected:
            conn.disconnect()

        logging.debug(
            'Connecting. Database: %s. User: %s', conn.database, conn.user
        )

        err = None
        hosts_num = len(conn.hosts)
        reconnect_counter = 0
        while reconnect_counter <= self.reconnect_attempts:
            host_rnd = random.randint(0, hosts_num - 1)
            (host, port) = conn.hosts[host_rnd]
            logging.debug('Connecting to %s:%s', host, port)
            reconnect_counter += 1
            try:
                res = conn._init_connection(host, port)
                reconnect_counter = 0
                return res

            except socket.timeout as e:
                conn.disconnect()
                logging.warning(
                    'Failed attempt #%s to connect to %s:%s', str(reconnect_counter), host, port, exc_info=True
                )
                err = errors.SocketTimeoutError(
                    '{} ({})'.format(e.strerror, conn.get_description())
                )

            except socket.error as e:
                conn.disconnect()
                logging.warning(
                    'Failed attempt #%s to connect to %s:%s', str(reconnect_counter), host, port, exc_info=True
                )
                err = errors.NetworkError(
                    '{} ({})'.format(e.strerror, conn.get_description())
                )

        if err is not None:
            raise err
