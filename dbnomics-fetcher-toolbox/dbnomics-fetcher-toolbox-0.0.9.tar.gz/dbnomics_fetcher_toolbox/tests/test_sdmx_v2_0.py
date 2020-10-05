# dbnomics-fetcher-toolbox
# Toolbox of functions and data types helping writing DBnomics fetchers.
# By: Christophe Benz <christophe.benz@cepremap.org>
#
# Copyright (C) 2019 Cepremap
# https://git.nomics.world/dbnomics/dbnomics-fetcher-toolbox
#
# dbnomics-fetcher-toolbox is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# dbnomics-fetcher-toolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Tests about ``sdmx_v2_0`` module."""


import pytest
from pydantic import ValidationError

from dbnomics_fetcher_toolbox.sdmx_v2_0 import NAN, Obs


def test_obs__float_value():
    """Test that it is possible to build an ``Obs`` with a ``float`` ``value``."""
    obs = Obs(value=1.2, attributes=[])
    assert obs.value == 1.2


def test_obs__nan_value():
    """Test that it is possible to build an ``Obs`` with a ``"NaN"`` ``value``."""
    obs = Obs(value=NAN, attributes=[])
    assert obs.value == NAN


def test_obs__str_value():
    """Test that it is not possible to build an ``Obs`` with a ``"foo"`` ``value``."""
    with pytest.raises(ValidationError):
        Obs(value="foo", attributes=[])
