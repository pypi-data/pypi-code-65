#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#

"""This file defines class CatagoryInfo, AttributeInfo and LabelTable."""

from enum import Enum
from typing import (
    Any,
    Dict,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    List,
    Mapping,
    Optional,
    Type,
    Union,
    ValuesView,
)

from ..label import LabelType
from ..utility import NameClass, NameSortedDict


class AttributeType(Enum):
    """All the possible type of the attributes."""

    boolean = bool
    integer = int
    number = float
    string = str
    array = list
    null = None
    instance = "instance"


class CategoryInfo(NameClass):
    """Information of a category, includes category name and description

    :param name: The name of the category
    :param loads: A dict contains all information of the category
    :raises
        TypeError: Name is required when not given loads
    """


class AttributeInfo(NameClass):
    """Information of a attribute

    :param name: The name of the attribute
    :param enum: All the possible values of the attribute
    :param attribute_type: The type of the attribute value
    :param minimum: The minimum value of number type attribute
    :param maximum: The maximum value of number type attribute
    :is_array: Whether the attribute is a sequence of values or not
    :param parent_categories: The parent categories of the attribute
    :param loads: A dict contains all information of the attribute
    :raises
        TypeError: Name and values are required when not given loads
    """

    SingleArgType = Union[
        str,
        None,
        Type[Any],
        AttributeType,
    ]
    ArgType = Union[SingleArgType, Iterable[SingleArgType]]

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        enum: Optional[Iterable[str]] = None,
        attribute_type: Optional[ArgType] = None,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        is_array: bool = False,
        parent_categories: Union[None, str, Iterable[str]] = None,
        loads: Optional[Dict[str, Any]] = None,
    ):
        if loads:
            super().__init__(loads=loads)
            self._parent_categories = loads.get("parentCategories", [])
            if loads.get("type", None) == "array":
                self._is_array = True
                schema = loads["items"]
            else:
                self._is_array = False
                schema = loads

            self._enum = schema.get("enum", None)
            self._type = self._convert_type(schema.get("type", None))
            self._minimum = schema.get("minimum", None)
            self._maximum = schema.get("maximum", None)
            return

        super().__init__(name)

        self._enum = enum
        self._type = self._convert_type(attribute_type)
        self._minimum = minimum
        self._maximum = maximum
        self._is_array = is_array

        if not parent_categories:
            self._parent_categories = []
        elif isinstance(parent_categories, str):
            self._parent_categories = [parent_categories]
        else:
            self._parent_categories = list(parent_categories)

    def _convert_type(self, type_: ArgType) -> Union[AttributeType, List[AttributeType], None]:
        if not type_:
            return None

        if isinstance(type_, Iterable) and not isinstance(type_, str):  # pylint: disable=W1116
            return [self._convert_single_type(single_type) for single_type in type_]

        return self._convert_single_type(type_)

    @staticmethod
    def _convert_single_type(type_: Union[str, Type[Any], AttributeType, None]) -> AttributeType:
        if isinstance(type_, str):
            return AttributeType[type_]

        if isinstance(type_, AttributeType):
            return type_

        return AttributeType(type_)

    def _dump_type(self) -> Union[str, List[str], None]:
        if isinstance(self._type, list):
            return [type_.name for type_ in self._type]

        if self._type:
            return self._type.name

        return None

    def dumps(self) -> Dict[str, Any]:
        """Dumps the information of this attribute as a dictionary.

        :return: A dictionary contains all information of this attribute
        """
        schema: Dict[str, Any] = {}
        if self._type:
            schema["type"] = self._dump_type()
        if self._enum:
            schema["enum"] = self._enum
        if self._minimum is not None:
            schema["minimum"] = self._minimum
        if self._maximum is not None:
            schema["maximum"] = self._maximum

        data: Dict[str, Any] = super().dumps()
        if self._is_array:
            data["type"] = "array"
            data["items"] = schema
        else:
            data.update(schema)
        if self._parent_categories:
            data["parentCategories"] = self._parent_categories
        return data


class LabelTable:
    """A table contains all labels in a specific label type

    :param is_tracking: A boolean value indicates whether corresponding table is tracking related
    :param loads: A dict contains all information of the label table
    """

    def __init__(
        self, is_tracking: bool = False, *, loads: Optional[Dict[str, Any]] = None
    ) -> None:
        self._categories: NameSortedDict[CategoryInfo] = NameSortedDict()
        self._attributes: NameSortedDict[AttributeInfo] = NameSortedDict()

        if loads:
            self._is_tracking: bool = loads.get("isTracking", False)
            self.description: Optional[str] = loads.get("description", None)
            for category in loads.get("categories", []):
                self.add_category(loads=category)
            for attribute in loads.get("attributes", []):
                self.add_attribute(loads=attribute)
            return

        self._is_tracking = is_tracking
        self.description = None

    def __str__(self) -> str:
        str_list = [f"{self.__class__.__name__}["]

        for category in self._categories.values():
            str_list.append(f"  {str(category)},")

        for attribute in self._attributes.values():
            str_list.append(f"  {str(attribute)},")

        str_list.append("]")

        return "\n".join(str_list)

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def is_tracking(self) -> bool:
        """Return whether the label is a tracking label

        :return: If it this a tracking label, return `True`, otherwise return `False`
        """
        return self._is_tracking

    @property
    def categories(self) -> NameSortedDict[CategoryInfo]:
        """Return all the categories of the LabelTable.

        :return: A NameSortedDict of all the categories
        """
        return self._categories

    def dumps(self) -> Dict[str, Any]:
        """Dumps the information of this LabelTable into a dictionary.

        :return: A dictionary contains all information of this LabelTable
        """
        data: Dict[str, Any] = {}

        categories = [category.dumps() for category in self._categories.values()]
        attributes = [attribute.dumps() for attribute in self._attributes.values()]

        if self._is_tracking:
            data["isTracking"] = self._is_tracking
        if self.description:
            data["description"] = self.description
        if categories:
            data["categories"] = categories
        if attributes:
            data["attributes"] = attributes

        return data

    def add_category(
        self, name: Optional[str] = None, *, loads: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a category to the LabelTable

        :param name: The name of the category
        :param loads: A dict contains all information of the category
        """
        self._categories.add(CategoryInfo(name, loads=loads))

    def add_attribute(
        self,
        name: Optional[str] = None,
        *,
        enum: Optional[Iterable[str]] = None,
        attribute_type: Optional[AttributeInfo.ArgType] = None,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        is_array: bool = False,
        parent_categories: Union[None, str, Iterable[str]] = None,
        loads: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a attribute to the LabelTable

        :param name: The name of the attribute
        :param enum: All the possible values of the attribute
        :param attribute_type: The type of the attribute value
        :param minimum: The minimum value of number type attribute
        :param maximum: The maximum value of number type attribute
        :is_array: Whether the attribute is a sequence of values or not
        :param parent_categories: The parent categories of the attribute
        :param loads: A dict contains all information of the attribute
        """
        self._attributes.add(
            AttributeInfo(
                name,
                enum=enum,
                attribute_type=attribute_type,
                minimum=minimum,
                maximum=maximum,
                is_array=is_array,
                parent_categories=parent_categories,
                loads=loads,
            )
        )


class LabelTables(Mapping[LabelType, LabelTable]):
    """Label tables is a mapping which contains `LabelTable`,
    the corresponding key is the 'name' of `LabelType`.

    :param loads: A dict contains a series of label tabel dicts

    """

    def __init__(self, *, loads: Optional[Dict[str, Any]] = None) -> None:
        self._data: Dict[LabelType, LabelTable] = {}

        if loads:
            for type_name, label_table in loads.items():
                self.create_label_table(LabelType[type_name], label_table)
            return

    def __getitem__(self, key: LabelType) -> LabelTable:
        return self._data.__getitem__(key)

    def __len__(self) -> int:
        return self._data.__len__()

    def __iter__(self) -> Iterator[LabelType]:
        return self._data.__iter__()

    def __str__(self) -> str:
        str_list = [f"{self.__class__.__name__}{{"]

        for label_type in self._data:
            str_list.append(f"  {label_type.name},")

        str_list.append("}")
        return "\n".join(str_list)

    def __repr__(self) -> str:
        return self.__str__()

    def create_label_table(
        self,
        label_type: LabelType,
        is_tracking: bool = False,
        *,
        loads: Optional[Dict[str, Any]] = None,
    ) -> LabelTable:
        """Create a new label table and add it to label tables.

        :param label_type: the label type of the label table
        :param is_tracking: A boolean value indicates whether corresponding task
                            is tracking related.
        :param loads: A dict contains all information of the label table

        :return: created new label table
        """

        label_table = LabelTable(is_tracking, loads=loads)
        self._data[label_type] = label_table
        return label_table

    def keys(self) -> KeysView[LabelType]:
        """Return keys view of the label tables' keys

        :return: keys view
        """
        return self._data.keys()

    def values(self) -> ValuesView[LabelTable]:
        """Return values view of the label tables' values.

        :return: values view
        """
        return self._data.values()

    def items(self) -> ItemsView[LabelType, LabelTable]:
        """Return items view of the label tables' items.

        :return: items view
        """
        return self._data.items()

    def dumps(self) -> Dict[str, Any]:
        """Dump the label tables into a series of label table dict.

        :return: a dict contains a series of label table dict with their label types as dict keys
        """
        label_table_dicts: Dict[str, Any] = {}
        for label_type, label_table in self._data.items():
            label_table_dicts[label_type.name] = label_table.dumps()
        return label_table_dicts
