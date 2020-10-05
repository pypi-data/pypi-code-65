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


"""Tests about ``data_model`` module."""


import pytest
from pydantic import ValidationError

from dbnomics_fetcher_toolbox.data_model import (
    Category,
    CategoryTree,
    DatasetReference,
    write_category_tree_json,
    write_series_jsonl,
)
from dbnomics_fetcher_toolbox.status import ResourceStatus


def test_category__code():
    """Test that a ``Category`` with a code is OK."""
    Category(code="C1", children=[])


def test_category__name():
    """Test that a ``Category`` with a name is OK."""
    Category(name="category 1", children=[])


def test_category__no_code_no_name():
    """Test that a ``Category`` with no code and no name fails."""
    with pytest.raises(ValidationError):
        Category(children=[])


def test_write_series_jsonl__no_series(tmp_path):
    """Test that an empty ``series.jsonl`` file is well written."""
    write_series_jsonl(tmp_path, [])
    file = tmp_path / "series.jsonl"
    assert file.is_file()
    assert file.read_text() == ""


def test_write_jsonl__some_series(tmp_path):
    """Test that a ``series.jsonl`` file with some series is well written."""
    write_series_jsonl(tmp_path, [{"code": "A.FR"}, {"code": "A.DE"}])
    file = tmp_path / "series.jsonl"
    assert file.is_file()
    assert (
        file.read_text() == '{"code":"A.DE"}\n{"code":"A.FR"}\n'
    ), "Series must be sorted by code"


def test_write_category_tree_json(tmp_path):
    """Test that a category tree is well written."""
    category_tree = CategoryTree(
        __root__=[
            Category(
                code="C1",
                children=[
                    DatasetReference(code="D1", status=ResourceStatus.SUCCESS),
                    DatasetReference(code="D2", status=ResourceStatus.FAILURE),
                ],
            ),
            Category(
                name="category 2",
                children=[
                    DatasetReference(code="D3", status=ResourceStatus.SUCCESS),
                    Category(code="C1", children=[]),
                ],
            ),
        ]
    )
    write_category_tree_json(tmp_path, category_tree)
    category_tree_2 = CategoryTree.parse_file(tmp_path / "category_tree.json")
    assert category_tree_2.__root__[0].code == "C1"
    assert category_tree_2.__root__[1].name == "category 2"
