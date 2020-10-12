import os
from typing import Optional
from dotenv import load_dotenv


def get_environment(key: str) -> Optional[str]:
    return os.getenv(key=key)


root_dir = str(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(dotenv_path=root_dir + "/.env")
