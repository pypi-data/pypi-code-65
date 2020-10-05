# -*- coding: utf-8 -*-
# This file is part of the pycalver project
# https://github.com/mbarkhau/pycalver
#
# Copyright (c) 2018-2020 Manuel Barkhau (mbarkhau@gmail.com) - MIT License
# SPDX-License-Identifier: MIT
# """Compose Regular Expressions from Patterns.

# >>> pattern = compile_pattern("vYYYY0M.BUILD[-TAG]")
# >>> version_info = pattern.regexp.match("v201712.0123-alpha")
# >>> assert version_info == {
# ...     "version": "v201712.0123-alpha",
# ...     "YYYY"   : "2017",
# ...     "0M"     : "12",
# ...     "BUILD"  : "0123",
# ...     "TAG"    : "alpha",
# ... }
# >>>
# >>> version_info = pattern.regexp.match("201712.1234")
# >>> assert version_info is None

# >>> version_info = pattern.regexp.match("v201712.1234")
# >>> assert version_info == {
# ...     "version": "v201712.0123-alpha",
# ...     "YYYY"   : "2017",
# ...     "0M"     : "12",
# ...     "BUILD"  : "0123",
# ...     "TAG"    : None,
# ... }
# """

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import re
import typing as typ
import pycalver.patterns as v1patterns
PATTERN_ESCAPES = [('\\', '\\\\'), ('-', '\\-'), ('.', '\\.'), ('+', '\\+'),
    ('*', '\\*'), ('?', '\\?'), ('{', '\\{'), ('}', '\\}'), ('[', '\\['), (
    ']', '\\]'), ('(', '\\('), (')', '\\)')]
PART_PATTERNS = {'YYYY': '[1-9][0-9]{3}', 'YY': '[1-9][0-9]?', '0Y':
    '[0-9]{2}', 'Q': '[1-4]', 'MM': '(?:[1-9]|1[0-2])', '0M':
    '(?:0[1-9]|1[0-2])', 'DD': '(?:[1-9]|[1-2][0-9]|3[0-1])', '0D':
    '(?:0[1-9]|[1-2][0-9]|3[0-1])', 'JJJ':
    '(?:[1-9]|[1-9][0-9]|[1-2][0-9][0-9]|3[0-5][0-9]|36[0-6])', '00J':
    '(?:00[1-9]|0[1-9][0-9]|[1-2][0-9][0-9]|3[0-5][0-9]|36[0-6])', 'WW':
    '(?:[0-9]|[1-4][0-9]|5[0-2])', '0W': '(?:[0-4][0-9]|5[0-2])', 'UU':
    '(?:[0-9]|[1-4][0-9]|5[0-2])', '0U': '(?:[0-4][0-9]|5[0-2])', 'VV':
    '(?:[1-9]|[1-4][0-9]|5[0-3])', '0V': '(?:0[1-9]|[1-4][0-9]|5[0-3])',
    'GGGG': '[1-9][0-9]{3}', 'GG': '[1-9][0-9]?', '0G': '[0-9]{2}', 'MAJOR':
    '[0-9]+', 'MINOR': '[0-9]+', 'PATCH': '[0-9]+', 'MICRO': '[0-9]+',
    'BUILD': '[0-9]+', 'TAG': '(?:alpha|beta|dev|rc|post|final)', 'PYTAG':
    '(?:a|b|dev|rc|post)?[0-9]*'}


def _replace_pattern_parts(pattern):
    for part_name, part_pattern in PART_PATTERNS.items():
        named_part_pattern = '(?P<{0}>{1})'.format(part_name, part_pattern)
        placeholder = '\\{' + part_name + '\\}'
        pattern = pattern.replace(placeholder, named_part_pattern)
    return pattern


def compile_pattern_str(pattern):
    for char, escaped in PATTERN_ESCAPES:
        pattern = pattern.replace(char, escaped)
    return _replace_pattern_parts(pattern)


def compile_pattern(pattern):
    pattern_str = compile_pattern_str(pattern)
    pattern_re = re.compile(pattern_str)
    return v1patterns.Pattern(pattern, pattern_re)
