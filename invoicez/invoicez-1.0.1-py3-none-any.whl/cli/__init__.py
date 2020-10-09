from functools import partial, wraps
from importlib import import_module, invalidate_caches as importlib_invalidate_caches
from logging import INFO
from pkgutil import walk_packages
from typing import Any, Callable

from click import (
    ClickException,
    group,
    option as click_option,
    Path as ClickPath,
)
from coloredlogs import install as coloredlogs_install

from invoicez.exceptions import InvoicezException


option = partial(click_option, show_default=True)

dir_path_option = option(
    "--dir-path",
    type=ClickPath(exists=True, readable=True, file_okay=False),
    default=".",
    help="Path of the deck.",
)


@group(chain=True)
def cli() -> None:
    coloredlogs_install(
        level=INFO, fmt="%(asctime)s %(name)s %(message)s", datefmt="%H:%M:%S",
    )


def command(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            result = f(*args, **kwargs)
        except InvoicezException as e:
            raise ClickException(str(e)) from e
        return result

    return cli.command()(wrapper)


def _import_module_and_submodules(package_name: str) -> None:
    """
    From https://github.com/allenai/allennlp/blob/master/allennlp/common/util.py
    """
    importlib_invalidate_caches()

    module = import_module(package_name)
    path = getattr(module, "__path__", [])
    path_string = "" if not path else path[0]

    for module_finder, name, _ in walk_packages(path):
        if path_string and module_finder.path != path_string:
            continue
        subpackage = f"{package_name}.{name}"
        _import_module_and_submodules(subpackage)


_import_module_and_submodules(__name__)
