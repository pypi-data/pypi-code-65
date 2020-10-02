# ======================================================================
# Copyright CERFACS (August 2019)
# Contributor: Adrien Suau (adrien.suau@cerfacs.fr)
#
# This software is governed by the CeCILL-B license under French law and
# abiding  by the  rules of  distribution of free software. You can use,
# modify  and/or  redistribute  the  software  under  the  terms  of the
# CeCILL-B license as circulated by CEA, CNRS and INRIA at the following
# URL "http://www.cecill.info".
#
# As a counterpart to the access to  the source code and rights to copy,
# modify and  redistribute granted  by the  license, users  are provided
# only with a limited warranty and  the software's author, the holder of
# the economic rights,  and the  successive licensors  have only limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using, modifying and/or  developing or reproducing  the
# software by the user in light of its specific status of free software,
# that  may mean  that it  is complicated  to manipulate,  and that also
# therefore  means that  it is reserved for  developers and  experienced
# professionals having in-depth  computer knowledge. Users are therefore
# encouraged  to load and  test  the software's  suitability as  regards
# their  requirements  in  conditions  enabling  the  security  of their
# systems  and/or  data to be  ensured and,  more generally,  to use and
# operate it in the same conditions as regards security.
#
# The fact that you  are presently reading this  means that you have had
# knowledge of the CeCILL-B license and that you accept its terms.
# ======================================================================

# See https://packaging.python.org/guides/creating-and-discovering-plugins/#using-naming-convention

import typing as ty
import types
import importlib
import pkgutil
import inspect
from collections.abc import MutableMapping


class LazyModuleLoader(MutableMapping):
    def __init__(self, prefix: str):
        self._prefix: str = prefix
        self._imported_keys: ty.Set[str] = set()
        self._mapping: ty.Dict[str, types.ModuleType] = dict()

    def _import_module_if_not_imported(self, item):
        if not inspect.ismodule(self._mapping[item]):
            try:
                self._mapping[item] = importlib.import_module(self._prefix + item)
                self._imported_keys.add(item)
            except ImportError:
                del self._mapping[item]

    def __setitem__(self, key: str, value: ty.Optional[types.ModuleType]) -> None:
        if not key.startswith(self._prefix):
            raise RuntimeError(
                f"Attempting to set the module '{key}' that does not "
                f"respect the given prefix '{self._prefix}'."
            )
        self._mapping[key[len(self._prefix) :]] = value

    def __delitem__(self, key: str) -> None:
        del self._mapping[key]

    def __getitem__(self, key: str) -> types.ModuleType:
        self._import_module_if_not_imported(key)
        return self._mapping[key]

    def __len__(self) -> int:
        return len(self._mapping)

    def __iter__(self) -> ty.Iterator[str]:
        return iter(self._mapping)

    def __repr__(self):
        return f"{type(self).__name__}({self._mapping})"

    def items(self):
        # First, iterate over the already imported modules
        for key in self._imported_keys:
            yield key, self[key]
        # Then, if needed, iterate over the other keys
        for key in filter(lambda k: k not in self._imported_keys, list(self.keys())):
            yield key, self[key]


frameworks = LazyModuleLoader(prefix="qprof_")
for package_info in pkgutil.iter_modules():
    name = package_info.name
    if name.startswith("qprof_"):
        frameworks[name] = None
