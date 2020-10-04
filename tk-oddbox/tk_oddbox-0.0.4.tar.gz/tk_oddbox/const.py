from pathlib import Path


class CharSet:
    """Some handy frozen sets of chars."""

    LOWER = frozenset("abcdefghijklmnopqrstuvwxyz")
    UPPER = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    LETTER = LOWER | UPPER
    DIGITS = frozenset("01234567890")
    UNDER = frozenset("_")
    IDENTIFIER = LETTER | DIGITS | UNDER


class WinDir:
    """Some handy directory paths for windows apps."""

    HOME = Path.home()
    APP_DATA = HOME.joinpath("AppData")
    LOCAL_APP_DATA = APP_DATA.joinpath("Local")
    ODDBOX = LOCAL_APP_DATA.joinpath("python_tk_oddbox")
