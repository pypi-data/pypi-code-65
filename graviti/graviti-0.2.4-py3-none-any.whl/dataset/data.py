#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#

"""This file defines class Data"""

import os
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
    Union,
    ValuesView,
    overload,
)

from typing_extensions import Literal

from ..label import (
    Classification,
    Label,
    LabeledBox2D,
    LabeledBox3D,
    LabeledPolygon2D,
    LabeledPolyline2D,
    LabelType,
)
from ..utility import TBRN

Labels = Union[
    Classification,
    List[LabeledBox2D],
    List[LabeledBox3D],
    List[LabeledPolygon2D],
    List[LabeledPolyline2D],
]


class Data(Mapping[LabelType, Labels]):
    """this class defines the concept of labels to one file

    :param fileuri: the file path of the labeled object in this data
    :param timestamp: the timestamp when collecting the labeled object in this data
    :param loads: {
        "fileuri": <str>,
        "timestamp": <float>,
        "labels_classification": {...},
        "labels_box2D": {...},
        "labels_box3D": {...},
        "labels_polygon": {...},
        "labels_polyline": {...},
    }
    :TypeError: when fileuri is not given
    """

    def __init__(
        self,
        fileuri: Union[str, TBRN, None] = None,
        *,
        remote_path: Optional[str] = None,
        timestamp: Optional[float] = None,
        loads: Optional[Dict[str, Any]] = None,
    ) -> None:

        self._labels: Dict[LabelType, Any] = {}
        self._remote_path = remote_path  # The remote storage location of the data

        if loads:
            fileuri = loads["fileuri"]
            timestamp = loads.get("timestamp", None)
            self.load_labels(loads)

        if not fileuri:
            raise TypeError(
                f"{self.__class__.__name__}() missing 1 required positional argument: 'fileuri'"
            )

        if isinstance(fileuri, str) and fileuri.startswith("tb:"):
            fileuri = TBRN(tbrn=fileuri)

        self._fileuri = fileuri
        self._timestamp = timestamp

        self._local_path = self._fileuri if isinstance(self._fileuri, str) else ""

    def dumps(self) -> Dict[str, Any]:
        """dump a data into a dict"""

        data_dict: Dict[str, Any] = {}
        data_dict["fileuri"] = str(self._fileuri)
        if self._timestamp is not None:
            data_dict["timestamp"] = self._timestamp

        data_dict.update(self.dump_labels())

        return data_dict

    def dump_labels(self) -> Dict[str, Any]:
        """dump all labels into a dict"""

        labels_dict: Dict[str, Any] = {}
        for key, labels in self._labels.items():
            if key == LabelType.CLASSIFICATION:
                labels_dict[key.value] = labels.dumps()
            else:
                labels_dict[key.value] = [label.dumps() for label in labels]

        return labels_dict

    def load_labels(self, loads: Dict[str, Any]) -> None:
        """load all labels into the data object"""

        for label_type in LabelType:
            if label_type.value not in loads:
                continue

            labels = loads[label_type.value]

            if label_type == LabelType.CLASSIFICATION:
                self._labels[label_type] = label_type.type(loads=labels)
            else:
                self._labels[label_type] = [label_type.type(loads=label) for label in labels]

    def __str__(self) -> str:
        return f'{self.__class__.__name__}("{self._fileuri}")'

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def fileuri(self) -> Union[str, TBRN]:
        """Return fileuri of the data.

        :return: fileuri of the data
        """
        return self._fileuri

    @property
    def timestamp(self) -> Optional[float]:
        """Return timestamp of the data.

        :return: timestamp of the data
        """
        return self._timestamp

    @property
    def tbrn(self) -> TBRN:
        """Return timestamp of the data.

        :return: timestamp of the data
        """
        if not isinstance(self._fileuri, TBRN):
            raise ValueError(f"{self.__str__()} has no TBRN")

        return self._fileuri

    @property
    def local_path(self) -> str:
        """Return local path of the data.

        :return: local path of the data
        """
        return self._local_path

    @property
    def remote_path(self) -> str:
        """Get the remote path of the data

        :return: the remote path of the data
        """
        if self._remote_path:
            return self._remote_path

        if isinstance(self._fileuri, TBRN):
            return self._fileuri.remote_path

        return os.path.basename(self._fileuri)

    @remote_path.setter
    def remote_path(self, remote_path: str) -> None:
        """Set the remote path of the data """
        self._remote_path = remote_path

    def register_label(self, label_types: Union[LabelType, Iterable[LabelType]]) -> None:
        """register one or several label types to data

        :param label_types: the LabelType to register
        """
        if not isinstance(label_types, Iterable):  # pylint: disable=W1116
            label_types = [label_types]

        for label_type in label_types:
            if label_type == LabelType.CLASSIFICATION:
                continue

            self._labels[label_type] = []

    def append_label(self, label: Label) -> None:
        """append a label to labels

        :param label: a Label to append
        :raises TypeError: when the label type of the append label is not registerd
        """

        if label.enum == LabelType.CLASSIFICATION:
            self._labels[label.enum] = label
            return

        try:
            self._labels[label.enum].append(label)
        except KeyError as error:
            raise TypeError(
                "LabelType needs to be registerd before appending label "
                f"(call register_label(LabelType.{label.enum.name}))"
            ) from error

    def __len__(self) -> int:
        return self._labels.__len__()

    def __iter__(self) -> Iterator[LabelType]:
        return self._labels.__iter__()

    @overload
    def __getitem__(self, label_type: Literal[LabelType.CLASSIFICATION]) -> Classification:
        ...

    @overload
    def __getitem__(self, label_type: Literal[LabelType.BOX2D]) -> List[LabeledBox2D]:
        ...

    @overload
    def __getitem__(self, label_type: Literal[LabelType.BOX3D]) -> List[LabeledBox3D]:
        ...

    @overload
    def __getitem__(self, label_type: Literal[LabelType.POLYGON]) -> List[LabeledPolygon2D]:
        ...

    @overload
    def __getitem__(self, label_type: Literal[LabelType.POLYLINE]) -> List[LabeledPolyline2D]:
        ...

    @overload
    def __getitem__(self, label_type: LabelType) -> Labels:
        ...

    def __getitem__(self, label_type: LabelType) -> Labels:
        """return one type of labels in a data

        :param label_type: required LabelType
        """
        return self._labels[label_type]  # type: ignore[no-any-return]

    def keys(self) -> KeysView[LabelType]:
        """A set-like object providing a view on the data label

        :return: keys view of data label
        """
        return self._labels.keys()

    def values(self) -> ValuesView[Labels]:
        """An object providing a view on the data label values

        :return: values view of the data label
        """
        return self._labels.values()

    def items(self) -> ItemsView[LabelType, Labels]:
        """A set-like object providing a view on the data label items

        :return: items view of the data label
        """
        return self._labels.items()
