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
from typing import Dict

import toolz.curried as toolz
import yaml

import orchid.version


_logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    pass


# Constants for environment variable names
ORCHID_ROOT_ENV_VAR = 'ORCHID_ROOT'
ORCHID_TRAINING_DATA_ENV_VAR = 'ORCHID_TRAINING_DATA'


def get_environment_configuration() -> Dict:
    """
    Gets the API configuration from the system environment.

    Returns:
        The configuration, if any, calculated from the system environment.
    """
    if ORCHID_ROOT_ENV_VAR in os.environ and ORCHID_TRAINING_DATA_ENV_VAR in os.environ:
        return {'orchid': {'root': os.environ[ORCHID_ROOT_ENV_VAR],
                           'training_data': os.environ[ORCHID_TRAINING_DATA_ENV_VAR]}}
    elif ORCHID_ROOT_ENV_VAR in os.environ:
        return {'orchid': {'root': os.environ[ORCHID_ROOT_ENV_VAR]}}
    elif ORCHID_TRAINING_DATA_ENV_VAR in os.environ:
        return {'orchid': {'training_data': os.environ[ORCHID_TRAINING_DATA_ENV_VAR]}}
    else:
        return {}


def get_fallback_configuration() -> Dict:
    """
    Returns final fallback API configuration.

    Returns:
        A Python dictionary with the default (always available configuration).

    Warning:
        Although we have striven to make the default configuration a working configuration, we can only ensure
        that the default configuration meets the minimal "syntax" required by the Python API. For example, if
        Orchid is **not** installed in the default location, and the `directory` key is not overridden by a
        higher priority configuration, the Python API will **fail** to load the Orchid assemblies and throw
        an exception at runtime.
    """

    # Symbolically, the standard location for the installed Orchid binaries is
    # `$ProgramFiles/Reveal Energy Services, Inc/Orchid/<version-specific-directory>`. The following code
    # calculates an actual location by substituting the current version number for the symbol,
    # `<version-specific-directory`.
    standard_orchid_dir = pathlib.Path(os.environ['ProgramFiles']).joinpath('Reveal Energy Services, Inc',
                                                                            'Orchid')
    version_id = orchid.version.Version().id()
    version_dirname = f'Orchid-{version_id.major}.{version_id.minor}.{version_id.patch}'
    default = {'orchid': {'root': str(standard_orchid_dir.joinpath(version_dirname))}}
    _logger.debug(f'default configuration={default}')
    return default


def get_file_configuration() -> Dict:
    """
    Returns the API configuration read from the file system.

    Returns:
        A python dictionary with the default (always available configuration).
    """

    # This code looks for the configuration file, `python_api.yaml`, in the `.orchid` sub-directory of the
    # user-specific (and system-specific) home directory. See the Python documentation of `home()` for
    # details.
    custom = {}
    custom_config_path = pathlib.Path.home().joinpath('.orchid', 'python_api.yaml')
    if custom_config_path.exists():
        with custom_config_path.open('r') as in_stream:
            custom = yaml.full_load(in_stream)
    _logger.debug(f'custom configuration={custom}')
    return custom


def python_api() -> Dict[str, str]:
    """
    Calculate the configuration for the Python API.

        Returns: The Python API configuration.
    """

    fallback_configuration = get_fallback_configuration()
    file_configuration = get_file_configuration()
    env_configuration = get_environment_configuration()

    result = toolz.merge(fallback_configuration, file_configuration, env_configuration)
    _logger.debug(f'result configuration={result}')
    return result


def training_data_path() -> pathlib.Path:
    """
    Returns the path of the directory containing the Orchid training data.

    Returns:
        The Orchid training data path.

    Raises:
        This function raises KeyError if the training directory path is not available from the package
        configuration.
    """
    result = pathlib.Path(toolz.get_in(['orchid', 'training_data'], python_api()))
    return result
