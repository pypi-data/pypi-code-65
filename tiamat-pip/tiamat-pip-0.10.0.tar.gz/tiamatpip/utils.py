"""
    tiamat.pip.utils
    ~~~~~~~~~~~~~~~~

    @todo: add description
"""
import os
import pathlib
import sys
from contextlib import contextmanager
from typing import Container
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from typing import Sequence

from pip._internal.utils import misc

from tiamatpip import configure

# Hold a reference to the real function
real_get_installed_distributions = misc.get_installed_distributions


@contextmanager
def changed_permissions(path: pathlib.Path, mode: int, skip: bool = False) -> Generator:
    if skip is False:
        previous_mode = path.stat().st_mode
    try:
        if skip is False:
            print("Setting mode {} to {}".format(oct(previous_mode | mode), path))
            for entry in path.rglob("*"):
                entry.chmod(previous_mode | mode)
        yield
    finally:
        if skip is False:
            print("Re-Setting mode {} to {}".format(oct(previous_mode), path))
            for entry in path.rglob("*"):
                entry.chmod(previous_mode)


@contextmanager
def patched_environ(
    *, environ: Optional[Dict[str, str]] = None, **kwargs: Dict[str, str]
) -> Generator:
    _environ = environ.copy() if environ else {}
    _environ.update(**kwargs)
    old_values = {}
    try:
        for key, value in _environ.items():
            if key in os.environ:
                old_values[key] = os.environ[key]
            os.environ[key] = value
        yield
    finally:
        for key in _environ:
            if key in old_values:
                os.environ[key] = old_values[key]
            else:
                os.environ.pop(key)


@contextmanager
def patched_sys_argv(argv: Sequence[str]) -> Generator:
    previous_sys_argv = list(sys.argv)
    try:
        sys.argv[:] = argv
        yield
    finally:
        sys.argv[:] = previous_sys_argv


def get_installed_distributions(
    local_only: bool = True,
    skip: Container[str] = misc.stdlib_pkgs,
    include_editables: bool = True,
    editables_only: bool = False,
    user_only: bool = False,
    paths: Optional[List[str]] = None,
):
    if f"{configure.ENVIRON_VARIABLE_NAME}_UNINSTALL" in os.environ:
        if paths is None:
            paths = []
        paths.append(configure.get_user_site_packages_path())
    return real_get_installed_distributions(
        local_only=local_only,
        skip=skip,
        include_editables=include_editables,
        editables_only=editables_only,
        user_only=user_only,
        paths=paths,
    )


def patch_pip_get_installed_distributions():
    misc.get_installed_distributions = get_installed_distributions
