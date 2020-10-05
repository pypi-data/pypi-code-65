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


"""Tests about ``formats`` module."""


from dbnomics_fetcher_toolbox.formats import write_jsonl


def test_write_jsonl__no_items(tmp_path):
    """Test that empty JSON Lines files is well written."""
    file = tmp_path / "my.jsonl"
    write_jsonl(file, [])
    assert file.is_file()
    assert file.read_text() == ""


def test_write_jsonl__some_items(tmp_path):
    """Test that JSON Lines files with some items is well written."""
    file = tmp_path / "my.jsonl"
    write_jsonl(file, [{"a": 1}, {"b": "hi"}])
    assert file.is_file()
    assert file.read_text() == '{"a":1}\n{"b":"hi"}\n'
