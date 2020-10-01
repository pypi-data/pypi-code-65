import collections.abc
import enum
import io
from typing import Any, IO, Iterator, List, Optional, Union, overload

from .typing import BencodeReturnObject, BencodeReturnObjectDecoded


class StrictError(ValueError):
    """Raised by :func:`load` and :func:`loads` when an exception that
    can be ignored by setting ``strict`` to ``False`` occurs
    """
    pass


class Delimiter(enum.IntEnum):
    """Bencode delimiter constants

    Contains all delimiters used in bencoded data with
    their corresponding ASCII code

    ``ZERO`` through ``NINE`` are sequential, meaning that you can use
    the following method to determine if `n` is an integer::

        Delimiter.ZERO <= n <= Delimiter.NINE

    :Attributes:
        ===== =====
        Attr  ASCII
        ===== =====
        DICT  ``d``
        LIST  ``l``
        INT   ``i``
        COLON ``:``
        END   ``e``
        MINUS ``-``

        ZERO  ``0``
        ONE   ``1``
        TWO   ``2``
        THREE ``3``
        FOUR  ``4``
        FIVE  ``5``
        SIX   ``6``
        SEVEN ``7``
        EIGHT ``8``
        NINE  ``9``
        ===== =====
    """
    DICT = ord(b'd')
    LIST = ord(b'l')
    INT = ord(b'i')
    COLON = ord(b':')
    END = ord(b'e')
    MINUS = ord(b'-')

    ZERO = ord(b'0')
    ONE = ord(b'1')
    TWO = ord(b'2')
    THREE = ord(b'3')
    FOUR = ord(b'4')
    FIVE = ord(b'5')
    SIX = ord(b'6')
    SEVEN = ord(b'7')
    EIGHT = ord(b'8')
    NINE = ord(b'9')


@overload
def load(
    file: IO[bytes], *,
    encoding: None = None, strict: bool = True
) -> BencodeReturnObject:
    ...
@overload
def load(
    file: IO[bytes], *,
    encoding: str, strict: bool = True
) -> BencodeReturnObjectDecoded:
    ...
def load(
    file: IO[bytes], *,
    encoding: Optional[str] = None, strict: bool = True
) -> Union[BencodeReturnObject, BencodeReturnObjectDecoded]:
    """Read a bencoded file, and convert it into a Python object

    :param file: the file to read the bencoded data from

        this should be a file object opened in binary read mode
        (``'rb'``)

    All other arguments and the return value are the same as in
    :func:`loads`

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

    bencode = file.read()
    return loads(bencode, encoding=encoding, strict=strict)


@overload
def loads(
    bencode: bytes, *,
    encoding: None = None, strict: bool = True
) -> BencodeReturnObject:
    ...
@overload
def loads(
    bencode: bytes, *,
    encoding: str, strict: bool = True
) -> BencodeReturnObjectDecoded:
    ...
def loads(
    bencode: bytes, *,
    encoding: Optional[str] = None, strict: bool = True
) -> Union[BencodeReturnObject, BencodeReturnObjectDecoded]:
    """Convert a bencoded byte string into a Python object

    :param bencode: the bencode byte string to convert
    :param strict:
        if ``True`` (default), :exc:`StrictError` will be raised if
        ``bencode`` contains any of the following:

        * an integer with leading zeros::

            b'i01e'

        * an integer that is negative zero::

            b'i-0e'

        * a dict where the keys are not in lexicographical order::

            b'd1:B3:VAL1:A3:VALe'

        If ``False``, the error will be ignored, and ``bencode`` will
        be converted anyway
    :param encoding:
        if provided, all byte strings will be decoded to unicode strings
        using the given encoding

        By default, all strings will be left as raw byte strings

        Only use this option if you're sure that ``bencode`` only
        contains strings that can be decoded using ``encoding``. It
        will raise an exception if unable to

    :return: the converted Python object
    :rtype:
        :data:`~benparse.typing.BencodeReturnObject` if ``encoding`` is
        ``None`` (default)

        :data:`~benparse.typing.BencodeReturnObjectDecoded` if
        ``encoding`` is given

    As long as ``strict`` is ``True`` and ``encoding`` is ``None``
    (default), you can safely reconvert the object back to bencode using
    :func:`dumps` without any data loss

    Examples:

    >>> loads(b'6:STRING')
    b'STRING'
    >>> loads(b'i12e')
    12
    >>> loads(b'd4:KEY15:VALUE4:KEY2i32ee')
    {b'KEY1': b'VALUE', b'KEY2': 32}
    # Using strict
    >>> loads(b'd1:B3:VAL1:A3:VALe')
    benparse.load.StrictError: index 9: dict is out of order. the key \
b'A' should come before the key b'B'
    >>> loads(b'd1:B3:VAL1:A3:VALe', strict=False)
    {b'B': b'VAL', b'A': b'VAL'}
    # Using encoding
    >>> loads(b'6:STRING')
    b'STRING'
    >>> loads(b'6:STRING', encoding='utf_8')
    'STRING'
    >>> # UTF-16 encoded strings
    >>> loads(b'l12:\\xff\\xfeI\\x00T\\x00E\\x00M\\x001\\x0012:\\xff\
\\xfeI\\x00T\\x00E\\x00M\\x002\\x0012:\\xff\\xfeI\\x00T\\x00E\\x00M\
\\x003\\x00e', encoding='utf_16')
    ('ITEM1', 'ITEM2', 'ITEM3')
    """
    if not isinstance(bencode, collections.abc.ByteString):
        raise TypeError(
            f'bencode must be a byte string. actual type: {type(bencode)}'
        )

    iterable = iter(range(len(bencode)))
    return _recursive_load(bencode, encoding, strict, iterable, _Mode.BASE)


class _Mode(enum.Enum):
    """Used internally by _recursive_load to keep track of what data
    type is currently being iterated over
    """
    BASE = enum.auto()
    LIST = enum.auto()
    DICT_KEY = enum.auto()
    DICT_VALUE = enum.auto()


def _assign_value(
    bencode: bytes, strict: bool, encoding: Optional[str], decode_bytes: bool,
    iterable: Iterator[int], mode: _Mode, value, obj, allow_setting_key: bool,
    index: int, last_key: Optional[bytes]
):
    """Adds ``value`` to ``obj`` based on the current mode, ``mode``

    ``bencode`` and ``iterable`` are passed to :func:`_recursive_load`
    to obtain the dict value when ``mode`` is ``DICT_KEY``

    ``strict`` is used to check dict keys as described in the docstring
    of :func:`loads`

    ``last_key`` should be set to the previous dict key when ``mode``
    is ``DICT_KEY``

    This is used to verify that the dict keys are in lexicographical
    order when ``strict`` is ``True``

    If ``last_key`` is ``None``, it is assumed that ``value`` is the
    first dict key

    If ``decode_bytes`` is ``True`` and ``encoding`` is not ``None``,
    ``value`` will be decoded to a unicode string using ``encoding``

    This should only be ``True`` when ``value`` is a byte string

    If ``allow_setting_key`` is ``True``, ``value`` can be set as a
    dict key. Otherwise, ``TypeError`` will be raised

    This should only be ``True`` when ``value`` is a byte string

    This is used to avoid setting invalid types as dict keys

    ``index`` is only used in error messages

    Return values:
      obj: same as ``obj``, but with the new ``value`` added to it
      break_loop: whether or not the function that called this function
        should break the recursive loop. This is set to ``True`` when
        ``mode`` is ``DICT_VALUE``
      last_key: the new ``last_key``. This is set to ``value`` when
        ``mode`` is ``DICT_KEY``. Otherwise, it's just set to
        ``last_key``
    """
    break_loop = False

    # bytes_value is used so that last_key is always a byte string even
    # if encoding is set
    bytes_value = value
    if decode_bytes and encoding is not None:
        value = bytes_value.decode(encoding)

    if mode is _Mode.BASE:
        if obj is not None:
            raise ValueError(
                f'index {index}: bencoded data contains multiple top-level '
                'values'
            )

        obj = value
    elif mode is _Mode.LIST:
        obj.append(value)
    elif mode is _Mode.DICT_VALUE:
        obj = value
        break_loop = True
    # mode is DICT_KEY
    else:
        if allow_setting_key:
            if value in obj:
                raise ValueError(f'index {index}: duplicate dict key: {value}')

            if strict and last_key is not None:
                if last_key > bytes_value:
                    raise StrictError(
                        f'index {index}: dict is out of order. the key '
                        f'{bytes_value!r} should come before the key '
                        f'{last_key!r}'
                    )
            last_key = bytes_value

            obj[value] = _recursive_load(
                bencode, encoding, strict, iterable, _Mode.DICT_VALUE
            )
        else:
            raise TypeError(
                f'index {index}: invalid type for a dict key. expected byte '
                'string'
            )

    return obj, break_loop, last_key


def _convert_int(bstr: bytes, index: int, strict: bool) -> int:
    """Converts the given string representation of an int to an actual
    int

    If ``strict`` is ``True``, the int is also checked as described in
    the docstring for :func:`loads`

    ``index`` is only used in error messages
    """
    if strict:
        if len(bstr) > 1 and bstr.startswith(b'0'):
            raise StrictError(
                f'index {index}: int cannot have leading zeros: {bstr!r}'
            )
        if bstr.startswith(b'-0'):
            raise StrictError(
                f'index {index}: zero cannot be negative: {bstr!r}'
            )

    return int(bstr)


def _recursive_load(
    bencode: bytes, encoding: Optional[str], strict: bool,
    iterable: Iterator[int], mode: _Mode
):
    """Recursive load function that is called by :func:`loads`

    ``iterable`` is used to iterate over ``bencode``. It should be
    created as follows:

    >>> iterable = iter(range(len(bencode)))

    ``mode`` is used to keep track of the current data type. It should
    be set to ``_Mode.BASE`` on the first run
    """
    obj: Union[BencodeReturnObject, List[Any]]
    if mode is _Mode.LIST:
        obj = []
    elif mode is _Mode.DICT_KEY:
        obj = {}
    else:
        obj = None

    # last_key is used to keep track of what the previous key was when
    # ``mode`` in order to ensure
    #
    # that dicts are in lexicographical order
    last_key = None
    # has_end_delimiter is used to detect unexpected end-of-strings due
    # to a missing ending
    #
    # delimiter or a string length that is too long
    has_end_delimiter = False

    for i in iterable:
        # dict
        if bencode[i] == Delimiter.DICT:
            dict_ = _recursive_load(
                bencode, encoding, strict, iterable, _Mode.DICT_KEY
            )
            last_key = None

            obj, break_loop, _ = _assign_value(
                bencode=bencode, strict=strict, encoding=encoding,
                decode_bytes=False, iterable=iterable, mode=mode, value=dict_,
                obj=obj, allow_setting_key=False, index=i, last_key=None
            )
            if break_loop:
                break
        # list
        elif bencode[i] == Delimiter.LIST:
            list_ = tuple(
                _recursive_load(
                    bencode, encoding, strict, iterable, _Mode.LIST
                )
            )

            obj, break_loop, _ = _assign_value(
                bencode=bencode, strict=strict, encoding=encoding,
                decode_bytes=False, iterable=iterable, mode=mode, value=list_,
                obj=obj, allow_setting_key=False, index=i, last_key=None
            )
            if break_loop:
                break
        # integer
        elif bencode[i] == Delimiter.INT:
            try:
                e = bencode.index(Delimiter.END, i)
            except ValueError as exception:
                # 'e' wasn't found
                raise ValueError(
                    f"index {i}: missing closing 'e' for integer value"
                ) from exception

            str_int = bencode[i+1:e]
            integer = _convert_int(bstr=str_int, index=i, strict=strict)

            # skip all iterations until after the 'e'
            for _ in range(e - i):
                next(iterable)

            obj, break_loop, _ = _assign_value(
                bencode=bencode, strict=strict, encoding=encoding,
                decode_bytes=False, iterable=iterable, mode=mode,
                value=integer, obj=obj, allow_setting_key=False, index=i,
                last_key=None
            )
            if break_loop:
                break
        # byte string
        elif (
            Delimiter.ZERO <= bencode[i] <= Delimiter.NINE
            or bencode[i] == Delimiter.MINUS
        ):
            try:
                colon = bencode.index(Delimiter.COLON, i)
            except ValueError as exception:
                # ':' wasn't found
                raise ValueError(
                    f"index {i}: missing delimiter ':' for byte string"
                ) from exception

            str_len = bencode[i:colon]
            length = _convert_int(bstr=str_len, index=i, strict=strict)
            if length < 0:
                raise ValueError(
                    f'index {i}: byte string length cannot be negative: '
                    f'{length}'
                )

            value = bencode[colon+1:colon+length+1]

            try:
                # skip all iterations until after the colon
                for _ in range(colon + length - i):
                    next(iterable)
            except StopIteration as exception:
                raise ValueError(
                    f'index {i}: reached end of string when reading byte '
                    f'string of length {length}'
                ) from exception

            obj, break_loop, last_key = _assign_value(
                bencode=bencode, strict=strict, encoding=encoding,
                decode_bytes=True, iterable=iterable, mode=mode, value=value,
                obj=obj, allow_setting_key=True, index=i, last_key=last_key
            )
            if break_loop:
                break
        # end of list/dict
        elif bencode[i] == Delimiter.END:
            if mode is _Mode.BASE:
                raise ValueError(f"index {i}: unexpected delimiter: 'e'")

            has_end_delimiter = True
            break
        else:
            raise ValueError(
                f'index {i}: unrecognized character: {bencode[i]}'
            )

    if not has_end_delimiter and mode not in (_Mode.BASE, _Mode.DICT_VALUE):
        raise ValueError(
            'unexpected end of string. this may be caused by a missing ending '
            "'e' delimiter, or by a mismatched number of dict keys and values"
        )

    return obj
