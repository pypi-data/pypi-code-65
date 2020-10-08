from paramiko.sftp_client import SFTPClient
from paramiko import Transport


class ClientSFTP:
    """ SFTP Client
    """

    def __init__(self, host, port, user, password):
        transport = Transport((host, port))
        transport.connect(None, user, password)
        self.client = SFTPClient.from_transport(transport)

    def get(self, remotepath, localpath, *args, **kwargs):
        self.client.get(remotepath, localpath, *args, **kwargs)
        self.client.close()

    def put(self, localpath, remotepath, *args, **kwargs):
        self.client.put(localpath, remotepath, *args, **kwargs)
        self.client.close()

    def get_latest(self, remotepath, localpath, *args, **kwargs):
        self.client.chdir(remotepath)
        ll = self.client.listdir_attr()
        ll.sort(key=lambda fileattr: fileattr.st_mtime)
        latest_file = ll[-1]
        self.get(latest_file.filename, localpath, *args, **kwargs)
