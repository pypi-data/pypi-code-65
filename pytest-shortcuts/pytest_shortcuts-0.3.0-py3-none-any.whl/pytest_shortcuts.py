import shlex

import dotenv
import pytest


def pytest_addoption(parser):
    parser.addini(
        "shortcuts",
        default=[],
        type="linelist",
        help=(
            "A colon-separated list of extra shortcut options "
            "and their expanded list of args"
        ),
    )
    parser.addoption(
        "--envfile", nargs="+", help="A file to an environment from via dotenv"
    )


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config, parser, args):
    """Expand any shortcuts in the command line arguments.

    The shortcuts are expanded very early so as to allow the edited options to be
    processed by other plugins/parts of pytest.

    It is also important to load the envfile early, in case any code relies on the
    environment. This will be too late for any Pytest plugins that rely on
    environment variables during module import.
    """
    shortcuts = dict(parse_shortcut(item) for item in early_config.getini("shortcuts"))

    add_command_line_options(shortcuts, parser)
    expand_shortcuts(shortcuts, args)

    for envfile in parse_envfiles_from_args_directly(args):
        load_envfile(envfile)


def parse_envfiles_from_args_directly(args):
    args = iter(args)

    for arg in args:
        if arg == "--envfile":
            filename = next(args)
            yield filename
        if arg.startswith("--envfile="):
            _, filename = arg.split("=", 1)
            yield filename


def add_command_line_options(shortcuts, parser):
    for shortcut, new_args in shortcuts.items():
        parser.addoption(
            shortcut,
            action="store_true",
            help="Shortcut for {}".format(" ".join(new_args)),
        )


def expand_shortcuts(shortcuts, raw_args):
    for shortcut, new_args in shortcuts.items():
        if shortcut in raw_args:
            pos = raw_args.index(shortcut)
            raw_args[pos : pos + 1] = new_args


def load_envfile(filename):
    path = dotenv.find_dotenv(
        filename=filename, raise_error_if_not_found=True, usecwd=True
    )
    dotenv.load_dotenv(path)


def parse_shortcut(item):
    assert ":" in item, "Invalid shortcut definition"
    key, val = item.split(":", 1)
    assert key.startswith("--"), "Invalid shortcut definition"
    shortcut = key.strip()
    args = shlex.split(val.strip())
    return (shortcut, args)
