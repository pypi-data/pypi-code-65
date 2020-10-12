import argparse
import os
import re
from typing import Dict, MutableMapping, NoReturn, Optional, Union
import warnings

import benparse

FilePath = Union[bytes, str]
"""Type used for file paths"""


class RTorrentMigrate:
    """Class for bulk-converting the data dir or session dir of
    rTorrent torrents

    The data dir is the dir that the torrent contents are saved to

    The session dir is the rtorrent session dir that the .torrent file
    is located in

    :param data_old: the current data dir that will be replaced
    :param data_new: the new data dir that ``data_old`` will be
        converted to

    :param session_old: the current session dir that will be replaced
    :param session_new: the new session dir that ``session_old`` will
        be converted to

    :param file_regex: only files that match this regex will be changed

        used by :func:`migrate_dir`

        default: ``'.+\\.torrent\\.rtorrent'``
    :param verbose: verbose output
    :param dry_run: do not save any changes made to disk

    Either ``data_old`` + ``data_new`` or ``session_old`` +
    ``session_new`` must be given

    If both are given, then both will be replaced

    :Example:

    >>> migrator = RTorrentMigrate(data_old='/torrents', \
data_new='/nas/torrents', verbose=True)
    >>> migrator.migrate_dir('.rtorrent_session', ignore_errors=True)
    """
    data_old: bytes
    data_new: bytes

    session_old: bytes
    session_new: bytes

    file_regex: str = r'.+\.torrent\.rtorrent'

    verbose: bool
    dry_run: bool

    def migrate(self, old_file: str, new_file: Optional[str] = None) -> None:
        """Convert a single file

        :param old_file: the file to read
        :param new_file:
            the file to save the modified output to. if ``new_file``
            isn't given, ``old_file`` will be overwritten
        """
        if new_file is None:
            new_file = old_file

        if self.verbose:
            print(f'reading file: {old_file}')

        with open(old_file, 'rb') as file:
            # assume that the bencode is formatted correctly
            bencode: Dict[bytes, bytes] = benparse.load(file)  # type: ignore

        data_changed = False
        session_changed = False

        if hasattr(self, 'data_old'):
            if self.verbose:
                current_value = self._decode_bytes(bencode[b'directory'])
                # '!r' is used because mypy complains about it being
                # omitted when `current_value` is a byte string
                print(f'\tcurrent data path: {current_value!r}')

            data_changed = self._bencode_replace(
                bencode, b'directory', self.data_old, self.data_new
            )

            if self.verbose and data_changed:
                new_value = self._decode_bytes(bencode[b'directory'])
                print(f'\t\tchanged to: {new_value!r}')
        if hasattr(self, 'session_old'):
            if self.verbose:
                current_value = self._decode_bytes(bencode[b'loaded_file'])
                print(f'\tcurrent session path: {current_value!r}')

            session_changed = self._bencode_replace(
                bencode, b'loaded_file', self.session_old, self.session_new
            )

            if self.verbose and session_changed:
                new_value = self._decode_bytes(bencode[b'loaded_file'])
                print(f'\t\tchanged to: {new_value!r}')

        if data_changed or session_changed:
            if not self.dry_run:
                if self.verbose:
                    print(f'\twriting to: {new_file}')
                with open(new_file, 'wb') as file:
                    benparse.dump(bencode, file)

    def migrate_dir(
        self, torrent_dir: str, *,
        file_regex: Optional[str] = None, ignore_errors: bool = False
    ) -> None:
        """Convert all files in a directory

        :param torrent_dir: the directory to walk through
        :param file_regex:
            only files matching this regex will be
            converted

            defaults to the value specified in the
            constructor

            only the base filename is matched; dir names are ignored

            the regex must match the entire filename
        :param ignore_errors:
            if ``True``, errors encountered when reading/parsing/writing
            files will not be fatal, and the function will move on to
            the next file
        """
        if file_regex is None:
            file_regex = self.file_regex

        if ignore_errors:
            onerror = self._warn_oserror
        else:
            onerror = self._raise_oserror

        if self.verbose:
            print(f'reading dir: {torrent_dir}')

        for root, _, files in os.walk(
            torrent_dir, onerror=onerror
        ):
            for file in files:
                if re.fullmatch(file_regex, file):
                    try:
                        self.migrate(os.path.join(root, file))
                    except Exception as exception:
                        if ignore_errors:
                            warnings.warn(f'{file}: {exception}')
                        else:
                            raise

    @staticmethod
    def _raise_oserror(exception: OSError) -> NoReturn:
        """Raises any errors generated by ``os.walk`` in
        :func:`migrate_dir`
        """
        raise exception

    @staticmethod
    def _warn_oserror(exception: OSError) -> None:
        """Raises a warning for any errors generated by ``os.walk`` in
        :func:`migrate_dir` and continues
        """
        warnings.warn(f'{exception.filename}: {exception}')

    @staticmethod
    def _decode_bytes(bytes_: bytes) -> Union[str, bytes]:
        """Attempt to decode the given byte string

        The default encoding is used (utf-8)

        If decoding fails, the original byte string is returned instead

        The purpose of this function is to decode file paths used in
        the output when ``verbose`` is `True`. The encoding is
        hard-coded to avoid confusion since it doesn't affect operation
        """
        try:
            return bytes_.decode()
        except UnicodeError:
            return bytes_

    @staticmethod
    def _bencode_replace(
        bencode: MutableMapping[bytes, bytes], key: bytes,
        old: bytes, new: bytes
    ) -> bool:
        """Replaces the value of ``key`` in ``bencode`` with ``new`` if
        it starts with ``old``

        Only ``old`` is replaced. The rest of the string is left as-is

        Raises ``KeyError`` if it can't find ``key``

        Returns ``True`` if the bencode was changed, otherwise ``False``

        The data directory corresponds to the key b'directory', and the
        session directory corresponds to the key b'loaded_file'
        """
        value = bencode[key]

        if value.startswith(old):
            new_value = new + value[len(old):]
            bencode[key] = new_value
            return True

        return False

    @staticmethod
    def _format_path(path: FilePath) -> bytes:
        """Converts ``path`` to bytes and adds a trailing slash

        The trailing slash is added to avoid partially replacing a dir
        name
        """
        if isinstance(path, str):
            path = path.encode()

        if not path.endswith(b'/'):
            path += b'/'

        return path

    def __init__(
        self, *,
        data_old: Optional[FilePath] = None,
        data_new: Optional[FilePath] = None,
        session_old: Optional[FilePath] = None,
        session_new: Optional[FilePath] = None,
        file_regex: Optional[str] = None,
        verbose: bool = False, dry_run: bool = False
    ):
        if (data_old is None) != (data_new is None):
            raise ValueError('data_old and data_new must both be defined')
        if (session_old is None) != (session_new is None):
            raise ValueError(
                'session_old and session_new must both be defined'
            )
        if data_old is None and session_old is None:
            raise ValueError(
                'not enough arguments. must provide data_old+data_new and/or '
                'session_old+session_new'
            )

        if data_old is not None:
            self.data_old = self._format_path(data_old)
        if data_new is not None:
            self.data_new = self._format_path(data_new)
        if session_old is not None:
            self.session_old = self._format_path(session_old)
        if session_new is not None:
            self.session_new = self._format_path(session_new)

        if file_regex is not None:
            self.file_regex = file_regex

        self.verbose = verbose
        self.dry_run = dry_run


def _get_parser(include_epilog: bool = False) -> argparse.ArgumentParser:
    """Returns the arg parser used by :func:`main`

    If ``include_epilog`` is `True`, the epilog of the parser will be
    set to a usage example. Otherwise, it won't have an epilog

    This option defaults to `False` because Sphinx has a dedicated page
    for examples, so sphinx-argparse doesn't need it
    """
    epilog = None
    if include_epilog:
        epilog = (
            'example: '
            '%(prog)s /path/to/dir -v --data /torrents /nas/torrents '
            '--session /torrents/.session /nas/.rtorrent'
        )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Migrate rTorrent torrents to a new path',
        epilog=epilog
    )

    parser.add_argument(
        'rtorrent_files', nargs='+',
        help='.rtorrent files to be changed. also accepts directories'
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='enables verbose output'
    )
    parser.add_argument(
        '-i', '--ignore', action='store_true',
        help=(
            'ignore errors when reading/writing files. continue to the next '
            'file instead of aborting'
        )
    )
    parser.add_argument(
        '-n', '--dry-run', action='store_true',
        help='perform a trial run with no changes made'
    )
    parser.add_argument(
        '-d', '--data', nargs=2, metavar=('OLD', 'NEW'),
        help='directory where the torrent contents are located'
    )
    parser.add_argument(
        '-s', '--session', nargs=2, metavar=('OLD', 'NEW'),
        help='rtorrent session directory where the .torrent files are located'
    )
    parser.add_argument(
        '-r', '--regex', default=RTorrentMigrate.file_regex,
        help='only files whose filename match this regex will be changed'
    )

    return parser


def _main() -> None:
    parser = _get_parser(True)
    args = parser.parse_args()

    if args.data is None and args.session is None:
        parser.error('--data and/or --session must be provided')

    kwargs = {}
    kwargs['verbose'] = args.verbose
    kwargs['dry_run'] = args.dry_run
    kwargs['file_regex'] = args.regex
    if args.data:
        kwargs['data_old'] = args.data[0]
        kwargs['data_new'] = args.data[1]
    if args.session:
        kwargs['session_old'] = args.session[0]
        kwargs['session_new'] = args.session[1]

    migrator = RTorrentMigrate(**kwargs)

    for file in args.rtorrent_files:
        if os.path.isdir(file):
            migrator.migrate_dir(file, ignore_errors=args.ignore)
        else:
            try:
                migrator.migrate(file)
            except Exception as exception:
                if args.ignore:
                    warnings.warn(f'{file}: {exception}')
                else:
                    raise
