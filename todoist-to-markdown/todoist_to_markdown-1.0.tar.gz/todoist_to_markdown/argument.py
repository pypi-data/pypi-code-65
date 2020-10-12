from typing import Optional, Dict, Any
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    'subcommand',
    help='必要な値を指定する',
    type=str,
    choices=['today'],
    default='today')
parser.add_argument(
    '-t', '--token',
    help='Todoistのトークンを指定します',
    type=str)
vars_args = vars(parser.parse_args())


def get_argument(key: str) -> Optional[Dict[str, Any]]:
    return vars_args[key] if key in vars_args else None
