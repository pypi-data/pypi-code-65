from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    method: str

    max_requests: int = None
    interval: int = 60
