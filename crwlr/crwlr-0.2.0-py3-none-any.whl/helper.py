#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from crwlr.statics import DASH, WHITESPACE, CROSSREF_DICTKEY_REFERENCETITLE


def check_re_match(regex, str_: str):
    """Check if the given regular expression matches (ignore case) the content of the given string

    Args:
        regex: a valid regular expression
        str_: a string

    Returns:
        bool: True for a match, False otherwise.

    """
    p = re.compile(regex, re.IGNORECASE)
    match = p.match(str_)
    res = match.group() if match else False

    return res


def get_fact_key(lang, date_id, author_id, medium_id):
    """Construct Fact key from arguments

    Args:
        lang: language dimension key (id)
        date_id: date dimension key (id)
        author_id: author dimension key (id)
        medium_id: medium dimention key (id)

    Returns:

    """
    return DASH.join([str(lang.lower()), str(date_id), author_id, medium_id])


def name_from(given_name, surname):
    """Construct name from given name and surname

    Args:
        given_name: the authors given name
        surname: the authors surname

    Returns: Both names separated by a whitespace

    """
    return WHITESPACE.join([given_name, surname])


def reference_title(reference):
    """Get the title of the reference from the cross ref dict.

    Note:
        There are multiple attribute names for the title of a publication in Crossref.
        Therefore, we iterate over a list of attribute names used by CrossRef to encode
        the title of a publication. The first hit is returned

    Args:
        reference: A parsed dict based on the CrossRef response

    Returns:
        str: the title of the publication if we found one
        bool: False if we did not find a valid title

    """
    for key in CROSSREF_DICTKEY_REFERENCETITLE:
        if key in reference:
            return reference[key]
    return False
