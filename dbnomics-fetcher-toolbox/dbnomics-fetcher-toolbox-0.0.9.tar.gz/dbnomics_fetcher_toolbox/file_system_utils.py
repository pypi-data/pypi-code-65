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

"""Utility functions about the file system."""

from pathlib import Path
from typing import Iterator


def iter_child_directories(
    directory: Path,
    include_hidden: bool = False,
) -> Iterator[Path]:
    """Yield child directories of ``directory``.

    If ``include_hidden=True``, don't skip child directories starting with a ``"."``.
    By default the value is ``False``, so that directories like ``.git`` are skipped.
    """
    for path in sorted(directory.iterdir()):
        if (include_hidden or not path.name.startswith(".")) and path.is_dir():
            yield path
