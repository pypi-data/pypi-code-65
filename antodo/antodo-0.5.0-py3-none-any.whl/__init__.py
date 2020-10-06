__all__ = ["main"]
__version__ = "0.5.0"

from .todo_cli import todo_cli


def main():
    todo_cli()
