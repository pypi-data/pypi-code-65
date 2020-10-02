import os
from typing import Optional, Dict, Any
import argparse

ENDPOINT = 'http://localhost:8000/analyse'


def get_environment(key: str) -> Optional[str]:
    return os.getenv(key=key)


def get_argument(key: str) -> Optional[Dict[str, Any]]:
    return vars_args[key] if key in vars_args else None


parser = argparse.ArgumentParser()
parser.add_argument(
    'url',
    type=str,)
parser.add_argument(
    '-t', '--translate',
    type=bool, default=False)
vars_args = vars(parser.parse_args())
