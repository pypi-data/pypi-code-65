import collections.abc
import io
from typing import Any, IO, Optional, overload

# Literal requires python 3.8+, but is backported to 3.5+ via the
# typing-extensions package
try:
    from typing import Literal
except ImportError:
    # ignore erroneous incompatible-import error from mypy
    # see https://github.com/python/mypy/issues/8319
    from typing_extensions import Literal  # type: ignore

from .typing import BencodeParamObject


@overload
def dump(
    obj: BencodeParamObject, file: IO[bytes], *,
    encoding: str = 'utf_8'
) -> None:
    ...
@overload
def dump(
    obj: Any, file: IO[bytes], *,
    skipinvalid: bool, encoding: str = 'utf_8'
) -> None:
    ...
def dump(
    obj: Any, file: IO[bytes], *,
    skipinvalid: bool = False, encoding: str = 'utf_8'
) -> None:
    """Convert a Python object into a bencoded byte string, and write
    the output to a file

    :param file: the file to dump the bencoded data to

        this should be a file object opened in binary write mode
        (``'wb'``)

    :return: ``None``

    All other arguments are the same as in :func:`dumps`

    :Example:

    >>> with open('testfile', 'wb') as file:
    ...     benparse.dump(b'BENCODE_STRING', file)
    ...
    >>> with open('testfile', 'rb') as file:
    ...     file.read()
    ...     _ = file.seek(0)
    ...     benparse.load(file)
    ...
    b'14:BENCODE_STRING'
    b'BENCODE_STRING'
    """
    if isinstance(file, io.TextIOBase):
        raise TypeError(f'file must be opened in binary mode: {file}')

    bencode = dumps(obj, skipinvalid=skipinvalid, encoding=encoding)
    file.write(bencode)


# ideally, `obj` should be a `BencodeParamObject` when `skipinvalid` is
# a literal False as well, but this doesn't seem to be possible. `bool`
# also matches a literal False, so the final overload where `obj` is
# `Any` will also match a literal False
@overload
def dumps(
    obj: BencodeParamObject, *,
    encoding: str = 'utf_8'
) -> bytes:
    ...
@overload
def dumps(
    obj: Any, *,
    skipinvalid: bool, encoding: str = 'utf_8'
) -> bytes:
    ...
def dumps(
    obj: Any, *,
    skipinvalid: bool = False, encoding: str = 'utf_8'
) -> bytes:
    """Convert a Python object into a bencoded byte string

    :param obj: the Python object to convert

        must be a combination of the following types:

            * mapping (``dict``)
            * sequence (``list``, ``tuple``)
            * byte string (``bytes``, ``bytearray``)
            * ``str``
            * ``int``
            * ``None`` (converted into an empty string. top-level only;
              cannot be within containers)

        Dict keys must be a byte string or string

        :Type:
            :data:`~benparse.typing.BencodeParamObject` if
            ``skipinvalid`` is ``False`` (default)

            ``Any`` if ``skipinvalid`` is ``True``
    :param encoding: any strings within ``obj`` will be converted into
        byte strings using this encoding
    :param skipinvalid: if ``True``, any objects within ``obj`` that
        are of an invalid type will be skipped and not included in the
        output instead of raising an exception

    :return: the converted bencoded byte string

    :Examples:

    >>> dumps(b'STRING')
    b'6:STRING'
    >>> dumps(12)
    b'i12e'
    >>> dumps( {'KEY1': 'VALUE', 'KEY2': 32} )
    b'd4:KEY15:VALUE4:KEY2i32ee'
    >>> # Using encoding
    >>> dumps( ['ITEM1', 'ITEM2', 'ITEM3'], encoding='utf_16' )
    b'l12:\\xff\\xfeI\\x00T\\x00E\\x00M\\x001\\x0012:\\xff\\xfeI\\x00T\
\\x00E\\x00M\\x002\\x0012:\\xff\\xfeI\\x00T\\x00E\\x00M\\x003\\x00e'
    >>> # Using skipinvalid
    >>> dumps( {'KEY1': 'VALUE', 'KEY2': 46.5} )
    TypeError: object '46.5' has an unsupported type: '<class 'float'>'
    >>> dumps( {'KEY1': 'VALUE', 'KEY2': 46.5}, skipinvalid=True )
    b'd4:KEY15:VALUEe'
    """
    return _recursive_dump(obj, encoding, skipinvalid, True)


@overload
def _recursive_dump(
    obj: Any, encoding: str, skipinvalid: bool, top_level: Literal[True]
) -> bytes:
    ...
@overload
def _recursive_dump(
    obj: Any, encoding: str, skipinvalid: bool, top_level: bool
) -> Optional[bytes]:
    ...
def _recursive_dump(
    obj: Any, encoding: str, skipinvalid: bool,
    top_level: bool
) -> Optional[bytes]:
    """Recursive dump function that is called by :func:`dumps`

    ``top_level`` is ``True`` when the function is only one level deep

    This is used to determine whether or not to return an empty byte
    string or ``None``

    Returns a bencoded byte string when the type of ``obj`` is valid

    Raises ``ValueError`` when the type of the given ``obj`` is invalid
    and ``skipinvalid`` is ``False``

    Returns ``None`` when the type of the given ``obj`` is invalid,
    ``skipinvalid`` is ``True``, and ``top_level`` is ``False``

    Returns an empty byte string when the type of ``obj`` is invalid,
    ``skipinvalid`` is ``True``, and ``top_level`` is ``True``

    Also returns an empty byte string when ``obj`` is ``None``, and
    ``top_level`` is ``True``

    This is done to match functionality with ``loads``, which converts
    empty strings to ``None``
    """
    # int
    if isinstance(obj, int):
        # delimiters are always ASCII encoded
        str_int = bytes(str(obj), 'ascii')
        return b'i' + str_int + b'e'
    # bytes or bytearray
    elif isinstance(obj, collections.abc.ByteString):
        # delimiters are always ASCII encoded
        str_len = bytes(str(len(obj)), 'ascii')
        # mypy complains about this because it thinks bytes and
        # ByteString aren't compatible
        #
        # see https://github.com/python/mypy/issues/8610
        return str_len + b':' + obj  # type: ignore
    # convert str to bytes
    elif isinstance(obj, str):
        bstr = bytes(str(obj), encoding)
        return _recursive_dump(bstr, encoding, skipinvalid, False)
    # sequence (list)
    elif isinstance(obj, collections.abc.Sequence):
        substr = b''

        for item in obj:
            converted = _recursive_dump(item, encoding, skipinvalid, False)
            # converted will be None when skipinvalid is True and item
            # had an invalid type
            if converted is not None:
                substr += converted

        return b'l' + substr + b'e'
    # mapping (dict)
    elif isinstance(obj, collections.abc.Mapping):
        converted_obj = {}
        substr = b''

        # ensure that all keys are a byte string
        #
        # this is done in a separate loop from below so that the below
        # loop can be sorted
        for key, value in obj.items():
            if isinstance(key, str):
                # convert str to bytes
                key = bytes(key, encoding)
            elif not isinstance(key, collections.abc.ByteString):
                if skipinvalid:
                    # skip the item because the key type is invalid
                    continue
                else:
                    raise TypeError(
                        f"dict key '{key}' is not a byte string. "
                        f'actual type: {type(key)}'
                    )

            # check if the converted unicode string conflicts with an
            # existing byte string
            #
            # example: {b'KEY': 'V1', 'KEY': 'V2'}
            if key in converted_obj:
                raise ValueError(
                    f"duplicate key, {key}, found in dict '{obj}' after "
                    'converting unicode strings to byte strings'
                )

            converted_obj[key] = value

        for key, value in sorted(converted_obj.items()):
            converted_key = _recursive_dump(key, encoding, skipinvalid, False)
            converted_value = _recursive_dump(
                value, encoding, skipinvalid, False
            )

            # converted_value will be None when skipinvalid is True and
            # value has an invalid type
            #
            # converted_key should never be None since it's type-checked
            # in the above loop, but mypy complains if we don't check it
            # here
            if converted_key is not None and converted_value is not None:
                substr += converted_key
                substr += converted_value

        return b'd' + substr + b'e'
    # None. return an empty string only if at the top level
    elif obj is None and top_level:
        return b''
    # unrecognized type. if skipinvalid is True, skip it. otherwise,
    # raise an exception
    else:
        if skipinvalid:
            if top_level:
                return b''
            else:
                return None
        else:
            raise TypeError(
                f"object '{obj}' has an unsupported type: '{type(obj)}'"
            )
