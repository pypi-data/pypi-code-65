import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from fire import Fire


class Vault:
    def __init__(self, password=None, path="vault.db"):
        self.path = path
        self.password = password
        self.vault = None
        if password is not None:
            self.__load(password, path)

    def __load(self, password, path):
        try:
            b64 = ""
            with open(path, "r") as vault_file:
                b64 = json.load(vault_file)

            nonce = b64decode(b64["nonce"])
            tag = b64decode(b64["tag"])
            data = b64decode(b64["data"])
            cipher = AES.new(b64decode(self.password), AES.MODE_EAX, nonce=nonce)
            raw_data = cipher.decrypt(data)

            cipher.verify(tag)
            self.vault = json.loads(raw_data)

        except FileNotFoundError:
            self.create({"place": "holder"})

    def view(self):
        print(self.vault)

    def keygen(self):
        return b64encode(get_random_bytes(32)).decode()

    def create(self, password=None, data=None):
        new_password = False
        if password is None:
            password = self.keygen()
            new_password = True

        self.password = password

        if data is None:
            # put random data as placeholder to avoid file been to the known value of {}
            self.vault = {self.keygen(): self.keygen()}
        else:
            self.vault = data
        self.save()
        if new_password:
            return password
        else:
            return None

    def get(self, key, default=None):
        return self.vault.get(key, default)

    def update(self, key, value):
        self.vault.update({key: value})
        self.save()

    def save(self):
        cipher = AES.new(b64decode(self.password), AES.MODE_EAX)
        nonce = cipher.nonce
        to_cipher = json.dumps(self.vault).encode()
        ciphertext, tag = cipher.encrypt_and_digest(to_cipher)
        result = json.dumps(
            {
                "nonce": b64encode(nonce).decode(),
                "tag": b64encode(tag).decode(),
                "data": b64encode(ciphertext).decode(),
            }
        )
        with open(self.path, "w") as vault_file:
            vault_file.write(result)


if __name__ == "__main__":
    Fire(Vault)
