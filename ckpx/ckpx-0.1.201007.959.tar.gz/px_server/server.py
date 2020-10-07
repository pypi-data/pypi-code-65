import os, stat, errno, subprocess, socket, platform
import logging
import time
from px_server.helper import download_and_extract_px_server_package

logging.getLogger().setLevel(logging.INFO)


class Server:

    __instance = None

    __instances = {}

    @staticmethod
    def get_instance(port=None):
        instance = None
        if port is None:
            if Server.__instance is None:
                Server.__instance = Server()
            instance = Server.__instance
        else:
            instance = Server.__instances[port]
            if instance is None:
                instance = Server(port)
                Server.__instances[port] = instance
        return instance

    port = None

    process = None

    px_server_executable_file_path = None

    def __init__(self, port=None):
        self.port = port
        self.setup()
        self.start()

    def __del__(self):
        self.stop()

    def setup(self):
        self.px_server_executable_file_path = download_and_extract_px_server_package()

    def start(self):

        if self.port is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("", 0))
            self.port = s.getsockname()[1]

        logging.info('Start px server from {} file on port {}'.format(self.px_server_executable_file_path, self.port))
        self.process = subprocess.Popen([self.px_server_executable_file_path, '--port', str(self.port)])
        time.sleep(1)

    def stop(self):
        if self.process is not None:
            logging.info('Stop px server')
            logging.info('Stop px server process {}'.format(self.process.pid))
            self.process.terminate()
            logging.info('px server stopped')
