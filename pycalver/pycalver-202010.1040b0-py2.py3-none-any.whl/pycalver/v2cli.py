#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the pycalver project
# https://github.com/mbarkhau/pycalver
#
# Copyright (c) 2018-2020 Manuel Barkhau (mbarkhau@gmail.com) - MIT License
# SPDX-License-Identifier: MIT
"""
CLI module for PyCalVer.

Provided subcommands: show, test, init, bump
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import typing as typ
import logging
from . import config
from . import version
from . import v2rewrite
from . import v2version
logger = logging.getLogger('pycalver.v2cli')


def update_cfg_from_vcs(cfg, all_tags):
    version_tags = [tag for tag in all_tags if v2version.is_valid(tag, cfg.
        version_pattern)]
    if not version_tags:
        logger.debug('no vcs tags found')
        return cfg
    version_tags.sort(reverse=True)
    _debug_tags = ', '.join(version_tags[:3])
    logger.debug('found tags: {0} ... ({1} in total)'.format(_debug_tags,
        len(version_tags)))
    latest_version_tag = version_tags[0]
    latest_version_pep440 = version.to_pep440(latest_version_tag)
    if latest_version_tag <= cfg.current_version:
        return cfg
    logger.info('Working dir version        : {0}'.format(cfg.current_version))
    logger.info('Latest version from VCS tag: {0}'.format(latest_version_tag))
    return cfg._replace(current_version=latest_version_tag, pep440_version=
        latest_version_pep440)


def get_diff(cfg, new_version):
    old_vinfo = v2version.parse_version_info(cfg.current_version, cfg.
        version_pattern)
    new_vinfo = v2version.parse_version_info(new_version, cfg.version_pattern)
    return v2rewrite.diff(old_vinfo, new_vinfo, cfg.file_patterns)
