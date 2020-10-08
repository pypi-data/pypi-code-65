from django.conf import settings
from .conf import include
from .exceptions import MissingSettingException


def get_menuconf():
    """
    Retrieves the root menu configuration file (ROOT_MENUCONF setting).

    :raise: MissingSettingException if the ROOT_MENUCONF setting is not defined.
    :return: The menu configuration module (ROOT_MENUCONF)
    """
    if not settings.ROOT_MENUCONF:
        raise MissingSettingException("Mandatory ROOT_MENUCONF setting is missing")
    return settings.ROOT_MENUCONF


def get_menu():
    """
    Read the menu configuration file(s) and returns the menu dictionary.

    :raise: MissingSettingException if the ROOT_MENUCONF setting is not defined.
    :return: The dictionary containing all menu elements.
    """
    menu = include(get_menuconf())
    return menu
