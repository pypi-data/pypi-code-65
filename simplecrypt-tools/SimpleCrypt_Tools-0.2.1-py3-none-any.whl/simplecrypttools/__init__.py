from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import base64
import io

class CryptTools:
    """SimpleCrypt provides easy methods to generate RSA key pair and encrypt/decrypt data with RSA key pair."""
    def __init__(self):
        self.maintainer = "Tal Ziv"
        self.github = "https://github.com/TalZiv/simplecrypt-tools"

    @staticmethod
    def generatekeypair(passphrase: str, key_size: int = 2048, debug: bool = False) -> dict:
        """Decrypt RSA encrypted base64 encoded data which is usful for web services.

            Args:
                b64_encoded_public_key = a RSA public key object.
                data = the data to be encrypted as bytes.
                debug = prints debug information.

            Return: RSA encrypted data encoded with base64.
        """
        if debug:
            print(passphrase)
            print(str(key_size))
        key = RSA.generate(key_size)
        key_data = {}
        key_data['private'] = key.exportKey(passphrase=passphrase, pkcs=8, protection="scryptAndAES128-CBC")
        key_data['public'] = key.publickey().exportKey()
        key_data['keysize'] = key_size
        return key_data

    @staticmethod
    def encrypt_with_rsa_key(publickey: bytes, data: bytes, debug: bool = False) -> bytes:
        """Decrypt RSA encrypted base64 encoded data which is usful for web services.

            Args:
                b64_encoded_public_key = a RSA public key object.
                data = the data to be encrypted as bytes.
                debug = prints debug information.

            Return: RSA encrypted data encoded with base64.
        """
        recipient_key = publickey
        session_key = get_random_bytes(16)
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        encryptedata = cipher_rsa.encrypt(session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)
        encryptedata += cipher_aes.nonce
        encryptedata += tag
        encryptedata += ciphertext
        if debug:
            print('Non encrypted Byte data: ' + str(data))
            print('before base64: ' + str(encryptedata))
        return encryptedata

    @staticmethod
    def decrypt_with_rsa_key(private_key: bytes, data: bytes, debug: bool = False) -> bytes:
        """Decrypt RSA encrypted encoded data.

            Args:
                private_key = a RSA public key object.
                data = the data to be encrypted as bytes.
                debug = prints debug information.

            Retrun: decrypted data as bytes.
        """
        if debug:
            print('Encrypted data as bytes BEFORE encoding: ' + str(data))
        tempio = io.BytesIO(data)
        # below is a list Comprehension with unpacking.
        enc_session_key, nonce, tag, ciphertext = [tempio.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1)]
        """
        enc_session_key = tempio.read(private_key.size_in_bytes())
        nonce = tempio.read(16)
        tag = tempio.read(16)
        ciphertext = tempio.read(-1)
        """
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        decrypted_data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        if debug:
            print('Encrypted data as bytes AFTER encoding: ' + str(data))
        return decrypted_data

    @staticmethod
    def encrypt_with_rsa_key_b64(b64_encoded_public_key: bytes, b64_data: bytes, debug: bytes = False) -> bytes:
        """Decrypt RSA encrypted base64 encoded data which is usful for web services.
            Args:
                b64_encoded_public_key = a RSA public key object encoded in base64.
                b64_data = data to be encrypted as base64 encoded bytes.
                debug = prints debug information.

            Return: RSA encrypted data encoded with base64.
        """
        recipient_key = RSA.import_key(base64.b64decode(b64_encoded_public_key))
        session_key = get_random_bytes(16)
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        encryptedata = cipher_rsa.encrypt(session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(base64.b64decode(b64_data))
        encryptedata += cipher_aes.nonce
        encryptedata += tag
        encryptedata += ciphertext
        if debug:
            print('Non encrypt b64_data: ' + str(b64_data))
            print('before base64: ' + str(encryptedata))
        return base64.b64encode(encryptedata)

    @staticmethod
    def decrypte_with_rsa_key_b64(b64_encoded_private_key: bytes, passphrase: str, b64_data: bytes, debug: bool = False) -> bytes:
        """Decrypt RSA encrypted data which is encoded in base64.
            Args:
                private_key = a RSA public key object.
                passphrase = the passphrase for the RSA key.
                data = data to be decrypted as base64 encoded bytes.
                debug = prints debug information.

            Return: RSA decrypted data encoded with base64.
        """
        private_key = RSA.import_key(base64.b64decode(b64_encoded_private_key), passphrase=passphrase)
        decoded = base64.b64decode(b64_data)
        if debug:
            print('Decoded base64 data: ' + str(decoded))
        tempio = io.BytesIO(decoded)
        # below is a list Comprehension with unpacking.
        enc_session_key, nonce, tag, ciphertext = [tempio.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1)]
        """
        enc_session_key = tempio.read(private_key.size_in_bytes())
        nonce = tempio.read(16)
        tag = tempio.read(16)
        ciphertext = tempio.read(-1)
        """
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        decrypted_data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        if debug:
            print('Decrypted data: ' + str(data))
        return base64.b64encode(decrypted_data)
