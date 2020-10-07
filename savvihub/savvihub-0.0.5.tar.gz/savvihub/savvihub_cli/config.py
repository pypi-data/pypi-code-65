from typing import Optional


class Config:
    token: Optional[str] = None
    parallel: int = 20

    experiment_id: int

config = Config()
