import logging
import os
import re
import shutil
from inspect import cleandoc
from pathlib import Path
from typing import Union, overload, Match, List

import yaml
from dicthandling import overlap_branches
from docopt import docopt, DocoptExit

__version__ = "0.1a1.post4"
__all__ = [
    "add_handler_once_per_session",
    "APath",
    "docopt_parsable",
    "handler_writing_logs_onto_console",
    "load_yaml_file_content",
    "remove_path_or_tree",
    "repr_posix_path",
    "strip_for_doctest",
    "try_decoding_potential_text_content",
    "update_yaml_file_content",
]

# create LOGGER with this namespace's name
_logger = logging.getLogger("myminions")
_logger.setLevel(logging.ERROR)
# create console handler and set level to debug
handler_writing_logs_onto_console = logging.StreamHandler()
# add formatter to ch
handler_writing_logs_onto_console.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s - %(module)s - %(funcName)s "
        "- %(lineno)s - %(levelname)s - %(message)s"
    )
)


APath = Union[str, Path, os.PathLike]


def add_handler_once_per_session(handler):
    """
    Avoid declaring the same handler multiple times, leading to multiple
    outputs of the same message.

    Args:
        handler:
            The handler to add.
    """

    def _same_handler_type_is_already_registered(
        searched_handler_type, logger: logging.Logger
    ) -> bool:
        for registered_handlers_of_this_session in logger.handlers:
            if isinstance(registered_handlers_of_this_session, searched_handler_type):
                return True
        return False

    global _logger
    current_handler = type(handler)
    if not _same_handler_type_is_already_registered(current_handler, _logger):
        _logger.addHandler(handler)


# Using the method for this module.
add_handler_once_per_session(handler_writing_logs_onto_console)


def docopt_parsable(func):
    """
    Parses arguments on base of function's docstring, which should apply to
    docopt. If successfully parsed the arguments are given to the decorated
    function. If unsuccessfully parsed full function's docstring is returned.
    """

    def wrapper(argv):
        args = None
        doc = cleandoc(func.__doc__)  # levels the intendations.
        try:
            args = docopt(doc, argv)
        except DocoptExit:
            # arguments were unsufficient, therefore show user the doc-string
            print(doc)
            return None
        return func(args)

    return wrapper


@overload
def repr_posix_path(any_path: str) -> str:
    pass


@overload
def repr_posix_path(any_path: Path) -> str:
    pass


_windows_drive_letter_matcher = re.compile("^([a-z]):")


def _replace_windows_drive_letter(drive_letter_match: Match) -> str:
    """
    Replaces the windows drive letter with a forward slash encapsulation.

    Notes:
        Is used by :func:`repr_posix_path` using :func:`re.sub`.

    Args:
        drive_letter_match(Match):
            The regular expression matched drive letter.

    Returns:
        str
    """
    drive_letter = drive_letter_match.group(1)
    return "/{}".format(drive_letter)


def repr_posix_path(any_path: Union[str, Path]) -> str:
    """
    Represents the path on a Windows machine as a Posix-Path representation
    turning back slashes to forward slashes.

    Examples:
        >>> repr_posix_path("c:\\\\a\\\\path")
        '/c/a/path'
        >>> repr_posix_path(".\\\\a\\\\path")
        './a/path'
        >>> repr_posix_path(".\\\\a\\\\path")
        './a/path'

    Args:
        any_path(str, Path):
            Any type of path representation.

    Returns:
        str
    """
    busted_windows_drive_letter = _windows_drive_letter_matcher.sub(
        _replace_windows_drive_letter, str(any_path)
    )
    return str(busted_windows_drive_letter).replace("\\", "/")


def strip_for_doctest(base_path_to_strip: APath, path_to_show: APath) -> str:
    """
    Strips the given *base path* from the *path to show* and performing
    :func:`repr_posix_path` on the result.

    Examples:
        >>> strip_for_doctest("/a/root/path", "/a/root/path/some/place")
        '... /some/place'

    Args:
        base_path_to_strip:
            The base path, which should be removed from the view.

        path_to_show:
            The path which is going to be viewed.

    Returns:
        str
    """
    stripped_path = str(path_to_show).replace(str(base_path_to_strip), "... ")
    return repr_posix_path(stripped_path)


def load_yaml_file_content(filepath: APath, default: dict = None) -> dict:
    """
    Load the yaml file content returning the parsed result.

    Args:
        filepath(Path):
            The file path of the yaml file, which should be loaded and parsed.

        default(dict):
            The default dict, which will be returned if the filepath doesn't
            exist.

    Returns:
        dict
    """
    assert filepath is not None, "filepath cannot be 'None'"
    assert default is None or isinstance(default, dict), "'default' must be a dict."

    try:
        yml_filpath = Path(filepath)
    except TypeError:
        raise ValueError("A valid filepath needs to be supplied. 'None' is not valid.")

    if not yml_filpath.exists():
        no_user_default_was_given_then_log_error = default is None
        if no_user_default_was_given_then_log_error:
            _logger.error(
                "'{}' was not found and therefore not loaded. "
                "An empty dict was returned instead. "
                "To turn this message off, either provide only existing file paths "
                "or explicitely define the argument `default` with an returning value."
                "".format(yml_filpath)
            )
            return {}
        else:
            if not isinstance(default, dict):
                raise TypeError("'default' must be a dictionary.")
            return default

    with open(yml_filpath, "rb") as yml_file:
        setup_binary_content = yml_file.read()
    upload_config_text = try_decoding_potential_text_content(setup_binary_content)
    external_setup = yaml.load(upload_config_text, Loader=yaml.SafeLoader)
    return external_setup


def update_yaml_file_content(filepath: APath, new_content: dict):
    """
    Updates the existing content of a yaml file with the *new content*. If the
    file does not exist a new file will be created.

    Notes:
        Overlapping values of new_content will override existing entries.
        Used method for merging the existing file content with the *new content*
        is :func:`dicthandling.overlap_branches`.

    Examples:
        >>> from tempfile import TemporaryDirectory
        >>> from pathlib import Path
        >>> with TemporaryDirectory() as tempdir:
        ...     temporary_filepath = Path(tempdir, "test.yml")
        ...     update_yaml_file_content(
        ...         temporary_filepath, {"a": 1, "b": {"de": "ep"}}
        ...     )
        ...     update_yaml_file_content(
        ...         temporary_filepath, {"b": {"de": {"eper": 2}}}
        ...     )
        ...     print(load_yaml_file_content(temporary_filepath))
        {'a': 1, 'b': {'de': {'eper': 2}}}

    Args:
        filepath(APath):
            The file path of the yaml file, which should be loaded and parsed.

        new_content(dict):
            The new content, which will be updated into the existing content.
            It should be parsable by pyyaml.
    """
    current_file_content = load_yaml_file_content(filepath, default={})
    updated_content = overlap_branches(current_file_content, new_content)
    with open(filepath, "w") as yaml_file:
        yaml.dump(updated_content, yaml_file)


_ENCODING_FORMAT_TRYOUTS = ["utf-8", "latin-1", "iso-8859-1", "windows-1252"]


def try_decoding_potential_text_content(
    byte_like_content, encoding_format_tryouts: List[str] = None
) -> str:
    """
    Tries to decode the given byte-like content as a text using the given
    encoding format types.

    Notes:
        The first choice is 'utf-8', but in case of different OS are involved,
        some json files might been created using a different encoding, leading
        to errors. Therefore this methods tries the encondings listed in
        *dicthandling._ENCODING_FORMAT_TRYOUTS* by default.

    Examples:
        >>> from dicthandling import try_decoding_potential_json_content
        >>> sample = '{"a": "test", "json": "string with german literals äöüß"}'
        >>> sample_latin_1 = sample.encode(encoding="latin-1")
        >>> sample_latin_1
        b'{"a": "test", "json": "string with german literals \xe4\xf6\xfc\xdf"}'
        >>> try_decoding_potential_text_content(sample_latin_1)
        '{"a": "test", "json": "string with german literals äöüß"}'
        >>> sample_windows = sample.encode(encoding="windows-1252")
        >>> sample_windows
        b'{"a": "test", "json": "string with german literals \xe4\xf6\xfc\xdf"}'
        >>> try_decoding_potential_text_content(sample_windows)
        '{"a": "test", "json": "string with german literals äöüß"}'

    Args:
        byte_like_content:
            The text as byte-like object, which should be decoded.

        encoding_format_tryouts: List[str]:
            Formats in which the text might be encoded.

    Raises:
        UnicodeDecodeError

    Returns:
        str:
            Hopefully a proper decoded text.
    """
    if encoding_format_tryouts is None:
        encoding_format_tryouts = _ENCODING_FORMAT_TRYOUTS
    return _try_decoding_content(byte_like_content, encoding_format_tryouts)


def _try_decoding_content(byte_like_content, encoding_format_tryouts: List[str]) -> str:
    """
    Tries to decode the given byte-like content as a text using the given
    encoding format types.

    Args:
        byte_like_content:
            The text as byte-like object, which should be decoded.

        encoding_format_tryouts: List[str]:
            Formats in which the text might be encoded.

    Raises:
        UnicodeDecodeError

    Returns:
        str:
            Hopefully a proper decoded text.
    """

    def _try_decoding_content_upon_error(
        byte_like_content, encoding_format_tryouts, last_error=None
    ):
        """
        Tries to encode the text until success. If every encoding format
        failed, then the last UnicodeDecodeError is raised.

        Args:
        byte_like_content:
            The text as byte-like object, which should be decoded.

        encoding_format_tryouts: List[str]:
            Formats in which the text might be encoded.

        last_error(optional):
            Last caught error.

        Returns:
            str:
                Hopefully a proper decoded text.
        """
        no_tried_format_succeeded = len(encoding_format_tryouts) == 0
        if no_tried_format_succeeded:
            raise last_error

        encoding_format = encoding_format_tryouts.pop(0)
        try:
            decoded_content = byte_like_content.decode(encoding_format)
            return decoded_content
        except UnicodeDecodeError as e:
            return _try_decoding_content_upon_error(
                byte_like_content, encoding_format_tryouts, e
            )

    format_tryouts = encoding_format_tryouts.copy()
    decoded_content = _try_decoding_content_upon_error(
        byte_like_content, format_tryouts
    )
    return decoded_content


def remove_path_or_tree(root_path_to_remove: APath):
    """
    Removes the path, either if it is just a path or a whole path tree.

    Examples:
        >>> import tempfile
        >>> from pathlib import Path
        >>> test_root_path = Path(tempfile.mkdtemp())
        >>> test_root_path.joinpath(".hidden").touch()
        >>> subfolder = test_root_path.joinpath("subfolder")
        >>> subfolder.mkdir()
        >>> subfolder.joinpath("subfile").touch()
        >>> subfolder.joinpath(".also_hidden").touch()
        >>> [path.name for path in test_root_path.rglob("*")]
        ['.hidden', 'subfolder', 'subfile', '.also_hidden']
        >>> remove_path_or_tree(root_path_to_remove=test_root_path)
        >>> test_root_path.exists()
        False
        >>> test_root_path = Path(tempfile.mkdtemp())
        >>> test_filepath = test_root_path.joinpath("test.file")
        >>> test_filepath.touch()
        >>> test_filepath.exists()
        True
        >>> remove_path_or_tree(test_filepath)
        >>> test_filepath.exists()
        False
        >>> remove_path_or_tree(test_root_path)
        >>> test_root_path.exists()
        False

    Raises:
        TypeError:
            If somethink else is providen than the expected a str, bytes or
            os.PathLike object.

    Args:
        root_path_to_remove(APath):
            Root path to remove.

    Returns:
        bool
    """
    root_path_to_remove = Path(root_path_to_remove)
    it_is_just_a_file_then_remove_it_and_exit = root_path_to_remove.is_file()
    if it_is_just_a_file_then_remove_it_and_exit:
        root_path_to_remove.unlink()
        return

    shutil.rmtree(str(root_path_to_remove))
