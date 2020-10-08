from importlib import import_module
from typing import Sequence
from .exceptions import (ConflictingArgumentException,
                         InvalidParameterTypeException,
                         MissingArgumentException)


def include(menuconf):
    if not isinstance(menuconf, str):
        raise InvalidParameterTypeException("menuconf must be of type 'str'")

    imported_module = import_module(menuconf)
    return getattr(imported_module, 'menu', {})


def label(name, **kwargs):
    if not isinstance(name, str):
        raise InvalidParameterTypeException("name must be of type 'str'")

    retval = kwargs
    retval.update({'type': 'label', 'name': name})
    return retval


def menu(name, viewname=None, url=None, **kwargs):
    if not isinstance(name, str):
        raise InvalidParameterTypeException("name must be of type 'str'")
    if viewname and not isinstance(viewname, str):
        raise InvalidParameterTypeException("viewname must be of type 'str'")
    if url and not isinstance(url, str):
        raise InvalidParameterTypeException("url must be of type 'str'")

    if not viewname and not url:
        raise MissingArgumentException('Either viewname or url argument must be present')
    if viewname and url:
        raise ConflictingArgumentException('Both viewname and url arguments must not be present')

    retval = kwargs
    retval.update({'type': 'menuentry', 'name': name})
    if viewname:
        retval['viewname'] = viewname
    if url:
        retval['url'] = url
    return retval


def menugroup(name, entries, **kwargs):
    if not isinstance(name, str):
        raise InvalidParameterTypeException("name must be of type 'str'")
    if not isinstance(entries, Sequence):
        raise InvalidParameterTypeException("entries must be a list of menu entries")

    retval = kwargs
    retval.update({'type': 'menugroup', 'name': name, 'entries': entries})
    return retval
