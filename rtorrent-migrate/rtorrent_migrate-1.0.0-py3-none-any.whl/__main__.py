"""Creates an RTorrentMigrate instance with the given command-line
arguments, and runs migrate/migrate_dir on all positional arguments
"""
from .migrator import _main

_main()
