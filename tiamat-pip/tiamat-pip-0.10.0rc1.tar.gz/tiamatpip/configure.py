"""
    tiamat.ip.configure
    ~~~~~~~~~~~~~~~~~~~

    Tiamat PIP configuration
"""
import os
import pathlib
import site
from typing import Optional
from typing import Union

# This environment variable is present whenever tiamatpip is
# intercepting pip calls
ENVIRON_VARIABLE_NAME: str = "TIAMAT_PIP_INSTALL"
__PIP_COMMAND_NAME: str = "pip"
__USER_SITE_PACKAGES_PATH: Optional[pathlib.Path] = os.environ.get(
    f"{ENVIRON_VARIABLE_NAME}_PYPATH"
)
if __USER_SITE_PACKAGES_PATH is not None:
    site.ENABLE_USER_SITE = True
    site.USER_BASE = __USER_SITE_PACKAGES_PATH


def set_user_site_packages_path(user_site_packages: Union[pathlib.Path, str]) -> None:
    if not isinstance(user_site_packages, pathlib.Path):
        user_site_packages = pathlib.Path(user_site_packages)
    global __USER_SITE_PACKAGES_PATH
    __USER_SITE_PACKAGES_PATH = user_site_packages
    site.ENABLE_USER_SITE = True
    site.USER_BASE = str(user_site_packages)


def get_user_site_packages_path() -> Optional[pathlib.Path]:
    global __USER_SITE_PACKAGES_PATH
    return __USER_SITE_PACKAGES_PATH


def set_pip_command_name(name: str) -> None:
    global __PIP_COMMAND_NAME
    __PIP_COMMAND_NAME = name


def get_pip_command_name() -> str:
    global __PIP_COMMAND_NAME
    return __PIP_COMMAND_NAME
