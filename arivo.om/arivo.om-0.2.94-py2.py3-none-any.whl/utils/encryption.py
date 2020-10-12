import json
import os
import threading

import pgpy
from om.utils import config
from redis import StrictRedis

_encryption = threading.local()


def get_encryption():
    global _encryption
    if not hasattr(_encryption, "val"):
        _encryption.val = Encryption()
    return _encryption.val


def encrypt_data(data, compress=True, key_name="default"):
    return get_encryption().encrypt_data(data, compress, key_name)


def encrypt_file(file_name, out_file_name=None, key_name="default"):
    return get_encryption().encrypt_file(file_name, out_file_name=out_file_name, key_name=key_name)


class Encryption:
    keys = {}
    fingerprints = {}
    REDIS_HKEY = "kv"
    REDIS_KEY_PREFIX = "encryption_key-"
    REDIS_DEFAULT_KEY = "encryption_key-default"
    locks = {}

    def __init__(self):
        self.redis = StrictRedis(host=config.string("REDIS_HOST", "localhost"),
                                 port=config.int("REDIS_PORT", 6379),
                                 db=config.int("REDIS_DB", 0))

    def get_key(self, key_name="default"):
        redis_key = self.REDIS_KEY_PREFIX + key_name
        lock = self.locks.get(key_name)
        if not lock:
            lock = threading.RLock()
            self.locks[key_name] = lock
        with lock:
            data = self.redis.hget(self.REDIS_HKEY, redis_key)
            if not data:
                return self.keys.get(key_name)
            new_key = json.loads(data)

            if new_key["fingerprint_id"] == self.fingerprints.get(key_name):
                return self.keys.get(key_name)

            self.keys[key_name], _ = pgpy.PGPKey.from_blob(new_key["pubkey"])
            self.fingerprints[key_name] = new_key["fingerprint_id"]
            return self.keys.get(key_name)

    def encrypt_file(self, file_name, out_file_name=None, key_name="default"):
        with open(file_name, "rb") as file:
            compress = True
            ending = file_name.rsplit(".", 1)
            if ending in ["gz", "jpg", "jpeg"]:
                compress = False
            encrypted = self.encrypt_data(file.read(), compress, key_name)
        if encrypted:
            new_name = out_file_name or f"{file_name}.pgp"
            if not new_name.endswith(".pgp"):
                new_name = new_name + ".pgp"
            with open(new_name, "wb") as out:
                out.write(encrypted)
            os.remove(file_name)
            return True
        return False

    def encrypt_data(self, data, compress=True, key_name="default"):
        compression = pgpy.constants.CompressionAlgorithm.ZLIB if compress else \
            pgpy.constants.CompressionAlgorithm.Uncompressed

        key = self.get_key(key_name)
        if not key:
            return None

        encrypted = key.encrypt(pgpy.PGPMessage.new(data), compression=compression)
        return bytes(encrypted)


if __name__ == "__main__":
    text = b"please decrypt me"
    encryption = Encryption()

    encrypted_text = encryption.encrypt_data(text, True)
    if encrypted_text:
        with open("/data/upload/files/test_encryption.txt.pgp", "wb") as outfile:
            outfile.write(encrypted_text)
    else:
        print("ENCRYPTION FAILED")

    with open("/data/test_encryption.txt", "wb") as new_file:
        new_file.write(text)
    encryption.encrypt_file("/data/test")
