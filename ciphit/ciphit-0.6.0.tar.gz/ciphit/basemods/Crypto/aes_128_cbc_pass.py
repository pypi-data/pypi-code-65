import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Aes_128_cbc_pass:
    backend = default_backend()
    iterations = 100_000

    def encrypt(self, text: str, password: str, iterations: int = None) -> str:
        if iterations is None:
            iterations = self.iterations
        assert isinstance(iterations, int)
        salt = secrets.token_bytes(16)
        key = self._derive_key(password.encode(), salt, iterations)
        return b64e(
            b"%b%b%b"
            % (
                salt,
                iterations.to_bytes(4, "big"),
                b64d(Fernet(key).encrypt(text.encode())),
            )
        ).decode()

    def decrypt(self, ctext: str, password: str) -> str:
        ctext = ctext.encode()
        decoded = b64d(ctext)
        salt, iter, ctext = decoded[:16], decoded[16:20], b64e(decoded[20:])
        iterations = int.from_bytes(iter, "big")
        key = self._derive_key(password.encode(), salt, iterations)
        return Fernet(key).decrypt(ctext).decode()

    def __init__(self) -> None:
        return

    def _derive_key(
        self,
        password: bytes,
        salt: bytes,
        iterations: int = None,
    ) -> bytes:
        """Derive a secret key from a given password and salt"""
        if iterations is None:
            iterations = self.iterations
        assert isinstance(iterations, int)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=self.backend,
        )
        return b64e(kdf.derive(password))
