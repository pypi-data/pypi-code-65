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

"""Functions and classes defining DBnomics data model."""

from operator import itemgetter
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Union

import ujson as json
from pydantic import BaseModel, root_validator
from typing_extensions import Literal

from .formats import write_json, write_jsonl
from .status import ResourceStatus

CATEGORY_TREE_JSON = "category_tree.json"
"""Name of the file containing data to represent a category tree."""

DATASET_JSON = "dataset.json"
"""Name of the file containing metadata about a dataset."""

PROVIDER_JSON = "provider.json"
"""Name of the file containing metadata about a provider."""

SERIES_JSONL = "series.jsonl"
"""Name of the file containing data about many time series."""

NA: Literal["NA"] = "NA"
"""Special value used when an observation value is `Not Available`."""


class SeriesError(ValueError):
    """An error with a series."""


class ObservationError(SeriesError):
    """An error with a series observation."""


class NoTimeDimensionError(SeriesError):
    """An error with the time dimension of a series."""


Value = Union[Literal["NA"], float]

# Category tree


class DatasetReference(BaseModel):
    """Represents a dataset node of a category tree."""

    code: str
    name: Optional[str]
    status: Optional[ResourceStatus]


CategoryTreeNode = Union["Category", DatasetReference]


class Category(BaseModel):
    """Represents a category node of a category tree."""

    children: List[CategoryTreeNode]
    code: Optional[str]
    name: Optional[str]
    doc_href: Optional[str]

    @root_validator
    def code_or_name_exist(cls, values):  # noqa
        if not values.get("code") and not values.get("name"):
            raise ValueError('One of "code" or "name" attributes must be defined')
        return values


class CategoryTree(BaseModel):
    """Represents a category tree of other categories or datasets pointers."""

    __root__: List[CategoryTreeNode]

    def to_json_data(self) -> List[dict]:
        """Return data as it would be encoded to JSON."""
        # This should be done by pydantic
        # Cf https://github.com/samuelcolvin/pydantic/issues/1008
        return json.loads(self.json(exclude_none=True))


def clean_category_tree_json(category_tree_json: List[dict]):
    """Clean category tree to remove SUCCESS statuses of dataset nodes recursively.

    Mutate ``category_tree_json``.
    """

    def visit(nodes: List[dict]):
        for node in nodes:
            if node.get("status") == ResourceStatus.SUCCESS.value:
                del node["status"]
            children = node.get("children")
            if children:
                visit(children)

    visit(category_tree_json)


def iter_dataset_references(category_tree: CategoryTree) -> Iterator[DatasetReference]:
    """Yield :class:`DatasetReference` objects from ``category_tree``.

    Category tree is iterated recursively.
    """

    def visit(nodes: List[CategoryTreeNode]) -> Iterator[DatasetReference]:
        for node in nodes:
            if isinstance(node, Category):
                yield from visit(node.children)
            else:
                assert isinstance(node, DatasetReference)
                yield node

    yield from visit(category_tree.__root__)


def write_category_tree_json(directory: Path, category_tree: CategoryTree):
    """Encode ``category_tree`` to JSON and write it to "category_tree.json".

    :param directory: The directory to write the file to.
    """
    json_data = category_tree.to_json_data()
    clean_category_tree_json(json_data)
    write_json(directory / CATEGORY_TREE_JSON, json_data)


# Series


def write_series_jsonl(directory: Path, series: Iterable[dict]):
    """Encode ``series`` to `JSON Lines`_ and write it to "series.jsonl".

    Each item of ``series`` must be a ``dict`` with a ``"code"`` key.

    ``series`` are sorted by ``"code"`` in order to guarantee a stable file.

    :param directory: write the file in this directory

    .. _JSON Lines: https://jsonlines.org/
    """
    return write_jsonl(directory / SERIES_JSONL, sorted(series, key=itemgetter("code")))
