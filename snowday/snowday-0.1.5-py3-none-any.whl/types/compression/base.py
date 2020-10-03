from dataclasses import dataclass


@dataclass
class Compression:
    method: str


NO_COMPRESSION = Compression(method="none")
