# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains definitions of agent components."""
import importlib.util
import logging
import sys
import types
from abc import ABC
from pathlib import Path
from typing import Optional

from aea.configurations.base import (
    ComponentConfiguration,
    ComponentId,
    ComponentType,
    PublicId,
)
from aea.exceptions import AEAEnforceError
from aea.helpers.logging import WithLogger


logger = logging.getLogger(__name__)


class Component(ABC, WithLogger):
    """Abstract class for an agent component."""

    def __init__(
        self,
        configuration: Optional[ComponentConfiguration] = None,
        is_vendor: bool = False,
        **kwargs,
    ):
        """
        Initialize a package.

        :param configuration: the package configuration.
        :param is_vendor: whether the package is vendorized.
        """
        WithLogger.__init__(self, **kwargs)
        self._configuration = configuration
        self._directory = None  # type: Optional[Path]
        self._is_vendor = is_vendor

    @property
    def component_type(self) -> ComponentType:
        """Get the component type."""
        return self.configuration.component_type

    @property
    def is_vendor(self) -> bool:
        """Get whether the component is vendorized or not."""
        return self._is_vendor

    @property
    def prefix_import_path(self):
        """Get the prefix import path for this component."""
        return self.configuration.prefix_import_path

    @property
    def component_id(self) -> ComponentId:
        """Ge the package id."""
        return self.configuration.component_id

    @property
    def public_id(self) -> PublicId:
        """Get the public id."""
        return self.configuration.public_id

    @property
    def configuration(self) -> ComponentConfiguration:
        """Get the component configuration."""
        if self._configuration is None:  # pragma: nocover
            raise ValueError("The component is not associated with a configuration.")
        return self._configuration

    @property
    def directory(self) -> Path:
        """Get the directory. Raise error if it has not been set yet."""
        if self._directory is None:
            raise ValueError("Directory not set yet.")
        return self._directory

    @directory.setter
    def directory(self, path: Path) -> None:
        """Set the directory. Raise error if already set."""
        if self._directory is not None:  # pragma: nocover
            raise ValueError("Directory already set.")
        self._directory = path


def load_aea_package(configuration: ComponentConfiguration) -> None:
    """
    Load the AEA package.

    It adds all the __init__.py modules into `sys.modules`.

    :param configuration: the configuration object.
    :return: None
    """
    dir_ = configuration.directory
    if dir_ is None:  # pragma: nocover
        raise AEAEnforceError("configuration directory does not exists.")

    # patch sys.modules with dummy modules
    prefix_root = "packages"
    prefix_author = prefix_root + f".{configuration.author}"
    prefix_pkg_type = prefix_author + f".{configuration.component_type.to_plural()}"
    prefix_pkg = prefix_pkg_type + f".{configuration.name}"
    sys.modules[prefix_root] = types.ModuleType(prefix_root)
    sys.modules[prefix_author] = types.ModuleType(prefix_author)
    sys.modules[prefix_pkg_type] = types.ModuleType(prefix_pkg_type)

    for subpackage_init_file in dir_.rglob("__init__.py"):
        parent_dir = subpackage_init_file.parent
        relative_parent_dir = parent_dir.relative_to(dir_)
        if relative_parent_dir == Path("."):
            # this handles the case when 'subpackage_init_file'
            # is path/to/package/__init__.py
            import_path = prefix_pkg
        else:
            import_path = prefix_pkg + "." + ".".join(relative_parent_dir.parts)

        spec = importlib.util.spec_from_file_location(import_path, subpackage_init_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[import_path] = module
        logger.debug(f"loading {import_path}: {module}")
        spec.loader.exec_module(module)  # type: ignore
