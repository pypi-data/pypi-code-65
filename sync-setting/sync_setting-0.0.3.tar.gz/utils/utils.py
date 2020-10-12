import dropbox
import configparser
from os import path


class TransferFile:
    def __init__(self, local_file_name, remote_file_name):
        self.local_file_name = local_file_name
        self.remote_file_name = remote_file_name
        self.sync = dropbox.Dropbox(
            oauth2_access_token=TransferFile.get_token())

    @staticmethod
    def get_token():
        config = configparser.ConfigParser()
        config.read(path.join(path.dirname(__file__),
                              "../", "config", "config.ini"))
        return config['dropbox']['token']

    def upload(self):
        with open(self.local_file_name, 'rb') as f:
            self.sync.files_upload(f.read(), self.remote_file_name)

    def download(self):
        _, resp = self.sync.files_download(self.remote_file_name)
        with open(self.local_file_name, 'wb') as f:
            f.write(resp.content)



