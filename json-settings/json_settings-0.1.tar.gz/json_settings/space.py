import itertools
import operator
import warnings

from collections.abc import Iterable

from copy import deepcopy

from functools import reduce

from typing import Type
from typing import Union 

from numpy import prod
from numpy import unravel_index

import json_settings as js


def custom_formatwarning(msg, *args, **kwargs):
    return "Warning: " + str(msg) + '\n'


warnings.formatwarning = custom_formatwarning


class Space:
    """Class that creates a tensor of settings objects from ranges.

    Given a settings object with :class:`~.Number` subsettings that are ranges,
    this class will construct a tensor where each element is a settings object
    with a particular value chosen for each range.

    Attributes
    ----------
    setting : :obj:`Type`[:class:`~.Settings`]
        The base settings object to be expanded.
    
    restrict : :obj:`dict`
        A dictionary of :obj:`str`: :obj:`str` pairs that are used to exclude
        subsetting branches from the exploration function for finding ranges.
        If when searching the settings object for ranges, a setting with the
        same name as a key in :attr:`restrict` is found, only subsettings with
        name equal to the corresponding key will be searched.
    
    """

    def __init__(self, setting: Type[js.Settings], restrict: js.StringDict):
        """The constructor for the :class:`Space` class.

        Parameters
        ----------
        setting : :obj:`Type`[:class:`~.Settings`]
            The settings object being expanded.

        restrict : :obj:`dict`[:obj:`str`, :obj:`str`]
            A dictionary of :obj:`str`: :obj:`str` pairs that are used to exclude
            subsetting branches from the exploration function for finding ranges.
            If when searching the settings object for ranges, a setting with the
            same name as a key in :attr:`restrict` is found, only subsettings with
            name equal to the corresponding key will be searched.

        """
        self.setting = setting
        self.restrict = restrict
        self.addresses = list()
        self.values = list()
        self.matched = dict()
        self.unmatched = list()
        self.space = list()
        self.explore(self.setting, list())
        self.build_space()

    def get_by_address(self, root: dict, address: js.StringList):
        return reduce(operator.getitem, address, root)

    def set_by_address(self, root: dict, address, value):
        self.get_by_address(root, address[:-1])[address[-1]] = value

    def explore(self, root, path, restrict = None):
        if issubclass(type(root), js.ListSetting):
            branch = enumerate(root.value)
        elif issubclass(type(root), js.DictionarySetting):
            branch = root.items()
        elif issubclass(type(root), js.Settings):
            branch = [(k, v) for k, v in root.__dict__.items() if "__" not in k]
        else:
            branch = list()
        if restrict:
            branch = [(k, v) for k, v in branch if k == restrict]
        for key, item in branch:
            new_path = deepcopy(path)
            if issubclass(type(item), js.NumberSetting):
                if item.is_range:
                    new_path.append(key)
                    if item.match:
                        if item.match in self.matched:
                            self.matched[item.match]["addresses"].append(new_path)
                            self.matched[item.match]["values"].append(item.get)
                        else:
                            self.matched[item.match] = {
                                "addresses": [new_path],
                                "values": [item.get] 
                            }
                    else:
                        self.unmatched.append(new_path)
                        self.addresses.append(new_path)
                        self.values.append(item.get)
            else:
                new_path.append(key)
                for k, v in self.restrict.items():
                    new_restrict = v if key == k else None
                    break
                self.explore(item, new_path, new_restrict)
   
    def build_space(self):
        for match, items in self.matched.items():
            self.addresses += items["addresses"]
            if len({len(i) for i in items["values"]}) != 1:
                warnings.warn(f"ranges with match id '{match}' have unequal "
                              f"length. Zipped to shortest.")
            self.values.append(list(zip(*items["values"])))
        for batch in itertools.product(*self.values):
            flat_batch = list()
            for item in batch:
                if isinstance(item, Iterable):
                    for subitem in item:
                        flat_batch.append(subitem)
                else:
                    flat_batch.append(item)
            rv = deepcopy(self.setting.__source__)
            for address, value in zip(self.addresses, flat_batch):
                self.set_by_address(rv, address, float(value))
            self.space.append(type(self.setting)(rv))

    def __getitem__(self, indices):
        if isinstance(indices, tuple):
            if len(indices) > len(self.values):
                raise IndexError(f"too many indices for array {self.shape}")
            for idx, item in enumerate(indices):
                if not isinstance(item, int):
                    raise IndexError("only integers are valid when accessing arrays")
                if not 0 <= item < self.shape[idx]:
                    raise IndexError(f"index {item} is out of bounds for axis "
                                     f"{idx} with size {self.shape[idx]}")
            index = 0
            for idx, item in enumerate(indices):
                index += item * int(prod([len(v) for v in self.values[idx + 1:]]))
        elif isinstance(indices, int):
            if len(self.values) > 1:
                raise IndexError(f"too many indices for array {self.shape}")
            if not 0 <= indices < self.shape[0]:
                raise IndexError(f"index {indices} is out of bounds for axis {0} "
                                 f"with size {self.shape[0]}")
            index = indices
        else:
            raise IndexError("only integers are valid when accessing arrays")

        return self.space[index]

    @property
    def shape(self):
        if len(self.values):
            return tuple((len(v) for v in self.values))
        else:
            return (1,)
        
    @property
    def zero(self) -> Union[Type[js.Settings], None]:
        if len(self.space) == 1:
            return self.space[0]
        else:
            return None
    
    @property
    def axes(self):
        for item, space in zip(self.addresses, self.values):
            print(self.build_path(item), space)

    def build_path(self, elements: js.StringList):
        rv = ""
        for item in elements:
            rv += f"{item} -> "
        return rv[:-4]
    
    def cout_summary(self):
        from textwrap import fill
        rv = ""
        rv += f"Computational space dimensions: " + f"{self.shape}\n"\
                .replace(",", " x")\
                .replace(")", "")\
                .replace("(", "")
        axis = 0
        for idx, item in enumerate(self.unmatched):
            rv += f"\naxis: {axis}:"
            rv += "\n"
            rv += f"\t{self.build_path(item)}"
            rv += "\n"
            rv += fill(f"\tvalues:  {self.values[idx]}\n",
                       width=70,
                       subsequent_indent="\t")
            axis += 1
        rv += "\n"
        for key, value in self.matched.items():
            rv += f"\naxis: {axis}:"
            rv += "\n"
            rv += f"\tmatch_id: {key}"
            for idx, item in enumerate(value["addresses"]):
                rv += "\n"
                rv += f"\t{self.build_path(item)}"
            rv += "\n"
            rv += fill(f"\tvalues: {list(zip(*value['values']))}",
                       width=70,
                       subsequent_indent="\t\t")
            axis += 1
        return rv
    
    def index(self, setting: Type[js.Settings]):
        linear_index = self.linear_index(setting) 
        return unravel_index(linear_index, self.shape)

    def linear_index(self, setting: Type[js.Settings]):
        return self.space.index(setting)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __len__(self):
        return len(self.space)

