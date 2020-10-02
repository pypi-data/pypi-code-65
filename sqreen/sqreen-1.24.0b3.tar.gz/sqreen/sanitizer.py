# -*- coding: utf-8 -*-
# Copyright (c) 2016 - 2020 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Sanitizer used to remove sensitive data from our payload"""

import logging
import re

from . import config
from .utils import HAS_TYPING, is_string, is_unicode

if HAS_TYPING:
    from typing import (
        AbstractSet,
        Any,
        FrozenSet,
        Iterable,
        Iterator,
        Mapping,
        MutableMapping,
        Pattern,
        Tuple,
    )
else:
    from collections import Iterable, Mapping


LOGGER = logging.getLogger(__name__)

MASK = '<Redacted by Sqreen>'


def compile_sensitive_regex():
    # type: () -> Pattern[str]
    try:
        pattern = config.CONFIG["STRIP_SENSITIVE_REGEX"]
        if not isinstance(pattern, str):
            raise TypeError
        return re.compile(pattern)
    except (TypeError, re.error):
        LOGGER.warning("Invalid regexp configuration: %r", config.CONFIG["STRIP_SENSITIVE_REGEX"])
        pattern = config.CONFIG_DEFAULT_VALUE["STRIP_SENSITIVE_REGEX"]
        if not isinstance(pattern, str):
            raise TypeError("Invalid default regex configuration")
        return re.compile(pattern)


SENSITIVE_KEYS = frozenset([k.strip().lower() for k in config.CONFIG["STRIP_SENSITIVE_KEYS"].split(',')])  # type: FrozenSet[str]
SENSITIVE_REGEX = compile_sensitive_regex()
LOGGER.debug("Using sensitive keys %s", ", ".join(SENSITIVE_KEYS))
LOGGER.debug("Using sensitive regex %s", SENSITIVE_REGEX.pattern)


def sanitize(data, sensitive_keys=SENSITIVE_KEYS,
             sensitive_regex=SENSITIVE_REGEX):
    # type: (Any, AbstractSet[str], Pattern[str]) -> Tuple[Any, bool]
    """
    Sanitize sensitive data from an object. Return a 2-tuple with a sanitized
    copy of the data and a boolean indicating if some data was removed.
    """
    sensitive_values = False

    if is_string(data):
        if not is_unicode(data):
            data = data.decode("utf-8", errors="replace")
        if sensitive_regex.search(data):
            data = MASK
            sensitive_values = True
        return data, sensitive_values

    elif isinstance(data, Mapping):
        new_dict = {}
        for k, v in data.items():
            if isinstance(k, str) and k.lower() in sensitive_keys:
                new_dict[k] = MASK
                sensitive_values = True
            else:
                ret_data, ret_sensitive = sanitize(
                    v, sensitive_keys=sensitive_keys,
                    sensitive_regex=sensitive_regex)
                new_dict[k] = ret_data
                sensitive_values |= ret_sensitive
        return new_dict, sensitive_values

    elif isinstance(data, Iterable):
        new_list = []
        for v in data:
            ret_data, ret_sensitive = sanitize(
                v, sensitive_keys=sensitive_keys,
                sensitive_regex=sensitive_regex)
            new_list.append(ret_data)
            sensitive_values |= ret_sensitive
        return new_list, sensitive_values

    return data, sensitive_values


def sanitize_attacks(attacks, sensitive_keys=SENSITIVE_KEYS,
                     sensitive_regex=SENSITIVE_REGEX):
    # type: (Iterable[MutableMapping], AbstractSet[str], Pattern[str]) -> Iterator[MutableMapping]
    """
    Sanitize sensitive data from a list of attacks. Return the sanitized
    attacks.
    """
    for attack in attacks:
        infos = attack.get("infos")
        if infos is None:
            continue

        waf_data = infos.get("waf_data")
        if waf_data is not None:
            new_waf_data = []
            for item in waf_data:
                filters = item.get("filter")
                if filters is None:
                    continue
                for filter_item in filters:
                    resolved_value = filter_item.get("resolved_value")
                    if isinstance(resolved_value, str) and sensitive_regex.search(resolved_value):
                        filter_item["match_status"] = MASK
                        filter_item["resolved_value"] = MASK
                        continue
                    key_path = filter_item.get("key_path")
                    if isinstance(key_path, Iterable):
                        for key in key_path:
                            if isinstance(key, str) and key.lower() in sensitive_keys:
                                filter_item["match_status"] = MASK
                                filter_item["resolved_value"] = MASK
                                break
                new_waf_data.append(item)
            infos["waf_data"] = new_waf_data
        else:
            attack["infos"], _ = sanitize(
                infos, sensitive_keys=sensitive_keys,
                sensitive_regex=sensitive_regex)
        yield attack


def sanitize_exceptions(exceptions, sensitive_values):
    # type: (Iterable[Mapping], bool) -> Iterator[Mapping]
    """
    Sanitize sensitive data from a list of exceptions. Return the sanitized
    exceptions.
    """
    for exc in exceptions:
        infos = exc.get("infos")
        if infos is not None:
            # We know the request contains PII, never send args
            # TODO more fine grained filtering
            args = infos.get("args")
            if args is not None and sensitive_values:
                infos.pop("args", None)

            waf_infos = infos.get("waf")
            if waf_infos is not None and sensitive_values:
                waf_infos.pop("args", None)

        yield exc
