#  Copyright 2017-2020 Reveal Energy Services, Inc 
#
#  Licensed under the Apache License, Version 2.0 (the "License"); 
#  you may not use this file except in compliance with the License. 
#  You may obtain a copy of the License at 
#
#      http://www.apache.org/licenses/LICENSE-2.0 
#
#  Unless required by applicable law or agreed to in writing, software 
#  distributed under the License is distributed on an "AS IS" BASIS, 
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
#  See the License for the specific language governing permissions and 
#  limitations under the License. 
#
# This file is part of Orchid and related technologies.
#

import logging
import os
import pathlib
import re
from typing import Dict

import toolz.curried as toolz
import yaml

import orchid.version


_logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    pass


@toolz.curry
def sort_installations(candidate_pattern, user_friendly_pattern, path):
    match_result = re.match(candidate_pattern, path.name)
    if not match_result:
        raise ConfigurationError(f'Expected directories matching {user_friendly_pattern} but found, "{str(path)}".')

    sortable_version = match_result.groups()
    return sortable_version


def python_api() -> Dict[str, str]:
    """
    Calculate the configuration for the Python API.

        Returns: The Python API configuration.

        BEWARE: The returned configuration will not have an 'directory' key if Orchid is neither installed
        nor configured with `$HOME/.orchid/python.yaml`.
    """

    # My general intent is that an actual user need not provide *any* configuration. Specifically,
    # I assume that the Orchid application is installed in the "standard" location,
    # `$ProgramFiles/Reveal Energy Services, Inc/Orchid/<version-specific-directory>`
    standard_orchid_dir = pathlib.Path(os.environ['ProgramFiles']).joinpath('Reveal Energy Services, Inc',
                                                                            'Orchid')
    version_id = orchid.version.Version().id()
    version_dirname = f'Orchid-{version_id.major}.{version_id.minor}.{version_id.patch}'
    default = {'directory': str(standard_orchid_dir.joinpath(version_dirname))}
    _logger.debug(f'default configuration={default}')

    # This code looks for the configuration file, `python_api.yaml`, in the `.orchid` sub-directory in the
    # user-specific home directory.
    custom = {}
    custom_config_path = pathlib.Path.home().joinpath('.orchid', 'python_api.yaml')
    if custom_config_path.exists():
        with custom_config_path.open('r') as in_stream:
            custom = yaml.full_load(in_stream)
    _logger.debug(f'custom configuration={custom}')

    result = toolz.merge(default, custom)
    _logger.debug(f'result configuration={result}')
    return result
