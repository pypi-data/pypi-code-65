from cryptography.fernet import Fernet
from typing import Tuple


class Aes_128_cbc:
    def encrypt(self, text: str, key=Fernet.generate_key()) -> Tuple[str, str]:
        return Fernet(key).encrypt(text.encode()).decode(), key.decode()

    def decrypt(self, ctext: str, key: str) -> str:
        return Fernet(key.encode()).decrypt(ctext.encode()).decode()

    def __init__(self) -> None:
        return
