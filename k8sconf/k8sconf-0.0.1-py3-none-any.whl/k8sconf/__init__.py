from glob import glob
import os


class Config:
    def __init__(self, secrets_path=False):
        self._secrets = {}

        if secrets_path:
            self._read_fs(secrets_path)

    def _read_fs(self, secrets_path):
        paths = glob(secrets_path.rstrip('/') + "/**")

        for secret in paths:
            with open(secret, 'r') as file:
                length = len(secret) - len(secrets_path.rstrip('/')+"/")
                secret_name = secret[-length:]
                self._secrets[secret_name] = file.read()

    def fetch(self, secret, default=False):
        if secret in self._secrets.keys():
            return self._secrets[secret]
        elif secret in os.environ.keys():
            return os.environ.get(secret)
        else:
            return default

    def add(self, list: dict):
        for secret, value in list.items():
            self._secrets[secret] = value
