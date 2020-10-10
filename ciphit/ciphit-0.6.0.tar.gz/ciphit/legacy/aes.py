from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random


class Crypt:
    def __init__(self, salt=Random.new().read(AES.block_size)):
        self.salt = salt
        self.enc_dec_method = "latin-1"

    def Encode(self, src, key, encode=True):
        src = src.encode()
        key = SHA256.new(key.encode()).digest()
        aes_obj = AES.new(key, AES.MODE_CBC, self.salt)
        padd = AES.block_size - len(src) % AES.block_size
        src += bytes([padd]) * padd
        hx_enc = self.salt + aes_obj.encrypt(src)
        return b64encode(hx_enc).decode(self.enc_dec_method) if encode else hx_enc

    def Decode(self, src, key, decode=True):
        if decode:
            str_tmp = b64decode(src.encode(self.enc_dec_method))
        key = SHA256.new(key.encode()).digest()
        salt = str_tmp[: AES.block_size]
        aes_obj = AES.new(key, AES.MODE_CBC, salt)
        str_dec = aes_obj.decrypt(str_tmp[AES.block_size :])
        padd = str_dec[-1]
        if str_dec[-padd:] != bytes([padd]) * padd:
            pass
        return str_dec[:-padd].decode(self.enc_dec_method)
