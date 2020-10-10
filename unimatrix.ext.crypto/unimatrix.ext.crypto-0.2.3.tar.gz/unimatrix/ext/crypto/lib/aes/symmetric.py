"""Declares :class:`AdvancedEncryptionStandardSymmetricKey`."""
import  os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ...ciphertext import CipherText
from ...symmetric import BaseSymmetricKey


class AdvancedEncryptionStandardSymmetricKey(BaseSymmetricKey):
    """An AES encryption key operating in GCM mode. The key material
    is kept in the local memory.
    """
    __module__ = 'unimatrix.ext.crypto.aes'
    capabilities = [
        'encrypt',
        'decrypt',
        'generate'
    ]

    @classmethod
    def generate(cls, length=256):
        """Generate a new AES key."""
        if length not in [128, 192, 256]:
            raise ValueError(f"Invalid bit length: {length}")
        return cls(AESGCM.generate_key(bit_length=length))

    def __init__(self, key):
        """Initialize a new :class:`AdvancedEncryptionStandardSymmetricKey`
        instance.

        Args:
            key (:class:`bytes`): a byte-sequence representing the private key.
        """
        self.__secret = key
        self.__key = AESGCM(key)

    def encrypt(self, blob, aad=None):
        """Encrypt `blob` using the symmetric encryption key.

        Args:
            blob (:class:`bytes`): the plaintext to encrypt, represented
                as a byte-sequences.
            aad (:class:`bytes`): Additional Authenticated Data (AAD) to
                include in the encryption. If `aad` is ``None``, then it
                defaults to an empty byte-sequence (``b''``).

        Returns:
            :class:`~unimatrix.ext.crypto.CipherText`
        """
        nonce = os.urandom(12)
        aad = aad or b''
        ct = CipherText(self.__key.encrypt(nonce, blob, aad))
        ct.update_annotations({
            'aes/nonce': bytes.hex(nonce),
            'aes/aad': bytes.hex(aad),
            'crypto/using': 'AESGCM',
        })
        return ct

    def decrypt(self, ct):
        """Decrypts a :class:`CipherText` instance using the private key.

        Args:
            ct (:class:`~unimatrix.ext.crypto.CipherText`): the cipher text
                to decrypt. The instance must provide the ``aes/nonce`` and
                ``aes/aad`` annotations.

        Returns:
            :class:`bytes`
        """
        if not ct.annotations.get('aes/nonce')\
        or not ct.annotations.get('crypto/using'):
            raise TypeError(
                f"Can not decrypt CipherText, missing annotations "
                f"in {ct.annotations}.")
        nonce = bytes.fromhex(ct.annotations['aes/nonce'])
        aad = bytes.fromhex(ct.annotations.get('aes/aad') or '')
        return self.__key.decrypt(nonce, bytes(ct), aad)

    def __bytes__(self):
        return self.__key
