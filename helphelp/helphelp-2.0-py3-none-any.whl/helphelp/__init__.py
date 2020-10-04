import argparse as ap
import importlib as imp
import logging as lg
import os
import pathlib as pl
import sys
from typing import *

import nestedtext as nt


PATH_ALIASES = pl.Path(os.environ.get("XDG_CONFIG_HOME", pl.Path("~/.config").expanduser())) / "pyh" / "aliases"
_log = lg.getLogger(__name__)
MAP_ALIASES = Mapping[str, str]
Module = type(os)


lg.basicConfig(level=lg.DEBUG)



def read_aliases() -> MAP_ALIASES:
    if PATH_ALIASES.is_file():
        try:
            _log.debug(f"Reading Nested Text from {PATH_ALIASES}")
            return nt.loads(PATH_ALIASES.read_text(encoding="utf-8"))
        except nt.NestedTextError as err:
            _log.error(f"Syntax error in alias file: {str(err)}")
            sys.exit(5)
    _log.debug("File {PATH_ALIASES} cannot be read (does it exist?).")
    return {}


def unalias(name: str, aliases: MAP_ALIASES) -> str:
    return aliases.get(name, name)


def module_aliased(name: str, aliases: MAP_ALIASES) -> str:
    name_module = unalias(name, aliases)
    if name_module != name:
        return f"{name_module} (alias {name})"
    return name


def import_module(name: str, aliases: MAP_ALIASES) -> Module:
    return imp.import_module(unalias(name, aliases))


def main():
    parser = ap.ArgumentParser("Get help on Python modules, classes and methods")
    parser.add_argument(
        "module",
        nargs="?",
        help=\
            "Module from which to take the construct to get help for. If omitted, either the construct is a "
            "module to get help for, or is built-in and requires no module import."
    )
    parser.add_argument(
        "construct",
        help="Module, class or function to get help for."
    )
    parser.add_argument(
        "--no-alias",
        action="store_false",
        dest="must_read_aliases",
        default=True,
        help=f"Skips reading the alias file at {PATH_ALIASES}."
    )
    args = parser.parse_args()

    aliases = {}
    if args.must_read_aliases:
        aliases = read_aliases()

    if args.module:
        try:
            module = import_module(args.module, aliases)
        except ImportError:
            _log.error(f"Module {module_aliased(args.module, aliases)} cannot be imported.")
            sys.exit(1)
        try:
            construct = eval(args.construct, module.__dict__)
        except AttributeError:
            _log.error(
                f"Construct {args.construct} is not an attribute of module {module_aliased(args.module, aliases)}."
            )
            sys.exit(2)
    else:
        try:
            construct = __builtins__[args.construct]
        except KeyError:
            try:
                construct = import_module(args.construct, aliases)
            except ImportError:
                _log.error(f"{args.construct} is neither a module, an alias nor a built-in construct.")
                sys.exit(2)

    help(construct)


if __name__ == "__main__":
    main()
