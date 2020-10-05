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


"""Tests about ``file_system_utils`` module."""


import pytest

from dbnomics_fetcher_toolbox.file_system_utils import iter_child_directories


@pytest.fixture
def dummy_provider_dir(tmp_path):
    """Return a dummy provider dir with a hidden dir inside to simulate ``.git``."""
    dir2 = tmp_path / "dir2"
    dir2.mkdir()
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    hidden_dir = tmp_path / ".hidden_dir"
    hidden_dir.mkdir()
    (tmp_path / "file1").write_text("hi")
    return tmp_path


def test_iter_child_directories__default(dummy_provider_dir):
    """Test that child directories are yielded alphabetically."""
    assert list(iter_child_directories(dummy_provider_dir)) == [
        dummy_provider_dir / "dir1",
        dummy_provider_dir / "dir2",
    ]


def test_iter_child_directories__include_hidden(dummy_provider_dir):
    """Test that ``include_hidden=True`` works."""
    assert list(iter_child_directories(dummy_provider_dir, include_hidden=True)) == [
        dummy_provider_dir / ".hidden_dir",
        dummy_provider_dir / "dir1",
        dummy_provider_dir / "dir2",
    ]
