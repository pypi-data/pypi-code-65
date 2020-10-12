"""Utility for changing your data and session directories of torrents
in rTorrent

Run ``rtorrent-migrate --help`` for command-line usage
"""

__all__ = ['RTorrentMigrate', 'FilePath']

from .migrator import RTorrentMigrate, FilePath
