# -*- coding: utf-8 -*-
# This file is part of the pycalver project
# https://github.com/mbarkhau/pycalver
#
# Copyright (c) 2018-2020 Manuel Barkhau (mbarkhau@gmail.com) - MIT License
# SPDX-License-Identifier: MIT
"""Rewrite files, updating occurences of version strings."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import io
import typing as typ
import logging
import pycalver2.version as v2version
import pycalver2.patterns as v2patterns
from pycalver import parse
try:
    import builtins
except ImportError:
    import __builtin__ as builtins
from pycalver import config
str = getattr(builtins, 'unicode', str)
from pycalver import rewrite as v1rewrite
logger = logging.getLogger('pycalver2.rewrite')


def rewrite_lines(pattern_strs, new_vinfo, old_lines):
    new_lines = old_lines[:]
    found_patterns = set()
    patterns = [v2patterns.compile_pattern(p) for p in pattern_strs]
    matches = parse.iter_matches(old_lines, patterns)
    for match in matches:
        found_patterns.add(match.pattern.raw)
        replacement = v2version.format_version(new_vinfo, match.pattern.raw)
        span_l, span_r = match.span
        new_line = match.line[:span_l] + replacement + match.line[span_r:]
        new_lines[match.lineno] = new_line
    non_matched_patterns = set(pattern_strs) - found_patterns
    if non_matched_patterns:
        for non_matched_pattern in non_matched_patterns:
            logger.error("No match for pattern '{0}'".format(
                non_matched_pattern))
            compiled_pattern_str = v2patterns.compile_pattern_str(
                non_matched_pattern)
            logger.error("Pattern compiles to regex '{0}'".format(
                compiled_pattern_str))
        raise v1rewrite.NoPatternMatch('Invalid pattern(s)')
    else:
        return new_lines


def rfd_from_content(pattern_strs, new_vinfo, content):
    line_sep = v1rewrite.detect_line_sep(content)
    old_lines = content.split(line_sep)
    new_lines = rewrite_lines(pattern_strs, new_vinfo, old_lines)
    return v1rewrite.RewrittenFileData('<path>', line_sep, old_lines, new_lines
        )


def iter_rewritten(file_patterns, new_vinfo):
    fobj = None
    for file_path, pattern_strs in v1rewrite.iter_file_paths(file_patterns):
        with file_path.open(mode='rt', encoding='utf-8') as fobj:
            content = fobj.read()
        rfd = rfd_from_content(pattern_strs, new_vinfo, content)
        yield rfd._replace(path=str(file_path))


def diff(new_vinfo, file_patterns):
    full_diff = ''
    fobj = None
    for file_path, pattern_strs in sorted(v1rewrite.iter_file_paths(
        file_patterns)):
        with file_path.open(mode='rt', encoding='utf-8') as fobj:
            content = fobj.read()
        try:
            rfd = rfd_from_content(pattern_strs, new_vinfo, content)
        except v1rewrite.NoPatternMatch:
            errmsg = "No patterns matched for '{0}'".format(file_path)
            raise v1rewrite.NoPatternMatch(errmsg)
        rfd = rfd._replace(path=str(file_path))
        lines = v1rewrite.diff_lines(rfd)
        if len(lines) == 0:
            errmsg = "No patterns matched for '{0}'".format(file_path)
            raise v1rewrite.NoPatternMatch(errmsg)
        full_diff += '\n'.join(lines) + '\n'
    full_diff = full_diff.rstrip('\n')
    return full_diff


def rewrite(file_patterns, new_vinfo):
    """Rewrite project files, updating each with the new version."""
    fobj = None
    for file_data in iter_rewritten(file_patterns, new_vinfo):
        new_content = file_data.line_sep.join(file_data.new_lines)
        with io.open(file_data.path, mode='wt', encoding='utf-8') as fobj:
            fobj.write(new_content)
