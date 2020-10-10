#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Pintaudi Giorgio

from enum import IntEnum
from typing import List


class DifIndex(IntEnum):
    """
    Enum representing a DIF index (as found in the DIF topology string)
    """
    WallMrdNorthTop = 0,
    WallMrdNorthBottom = 1,
    WallMrdSouthTop = 2,
    WallMrdSouthBottom = 3,
    WagasciUpstreamTop = 4,
    WagasciUpstreamBottom = 5,
    WagasciDownstreamTop = 6
    WagasciDownstreamBottom = 7

    @classmethod
    def is_wallmrd(cls, index):
        # type: (int) -> bool
        """
        :param index: DIF index
        :return: true if the DIF belongs to a WallMRD
        """
        return index in [int(cls.WallMrdNorthTop), int(cls.WallMrdNorthBottom),
                         int(cls.WallMrdSouthTop), int(cls.WallMrdSouthBottom)]

    @classmethod
    def is_wallmrd_north(cls, index):
        # type: (int) -> bool
        """
        :param index: DIF index
        :return: true if the DIF belongs to the north WallMRD
        """
        return index in [int(cls.WallMrdNorthTop), int(cls.WallMrdNorthBottom)]

    @classmethod
    def is_wallmrd_south(cls, index):
        # type: (int) -> bool
        """
        :param index: DIF index
        :return: true if the DIF belongs to the south WallMRD
        """
        return index in [int(cls.WallMrdSouthTop), int(cls.WallMrdSouthBottom)]

    @classmethod
    def is_wagasci(cls, index):
        # type: (int) -> bool
        """
        :param index: DIF index
        :return: true if the DIF belongs to a WallMRD
        """
        return index in [int(cls.WagasciUpstreamTop), int(cls.WagasciUpstreamBottom),
                         int(cls.WagasciDownstreamTop), int(cls.WagasciDownstreamBottom)]

    @classmethod
    def is_wagasci_upstream(cls, index):
        # type: (int) -> bool
        """
        :param index: DIF index
        :return: true if the DIF belongs to the north WallMRD
        """
        return index in [int(cls.WagasciUpstreamTop), int(cls.WagasciUpstreamBottom)]

    @classmethod
    def is_wagasci_downstream(cls, index):
        # type: (int) -> bool
        """
        :param index: DIF index
        :return: true if the DIF belongs to the south WallMRD
        """
        return index in [int(cls.WagasciDownstreamTop), int(cls.WagasciDownstreamBottom)]


class DetectorIndex(IntEnum):
    """
    Enum representing an arbitrary detector index
    """
    WallMrdNorth = 0,
    WallMrdSouth = 1,
    WagasciUpstream = 2,
    WagasciDownstream = 3


class DetectorType(IntEnum):
    """
    Enum representing an arbitrary detector type (WAGASCI or WallMRD)
    """
    Wagasci = 1
    Wallmrd = 2


class State(object):
    """
    State of a sub-detector or of a DIF
    """
    def __init__(self, name, enabled, is_dif):
        # type: (str, bool, bool) -> None
        """
        :param name: name of the sub-detector or DIF
        :param enabled: True if you want to enable it
        :param is_dif: True if is a DIF, False if it is a whole sub-detector
        """
        self.name = name
        self._enabled = enabled
        self._is_dif = is_dif

    def is_enabled(self):
        # type: (...) -> bool
        """
        :return: True if is enabled
        """
        return self._enabled

    def enable(self):
        # type: (...) -> None
        """
        Enable the sub-detector of DIF
        :return: None
        """
        self._enabled = True

    def disable(self):
        # type: (...) -> None
        """
        Disable the sub-detector of DIF
        :return: None
        """
        self._enabled = False

    def is_dif(self):
        # type: (...) -> bool
        """
        :return: True if this object represents a DIF, False if it represents a whole sub-detector
        """
        return self._is_dif


class Topology(object):
    """List of _enabled and disabled detectors. If the flag '_iterate_by_dif' is disabled (default) the iterator
       iterates through the subdetectors. If the flag is _enabled the iterator iterates throught each DIF of the
       subdetectors."""

    def __init__(self, iterate_by_dif=False):
        # type: (bool) -> None
        """
        :param iterate_by_dif: True if you want the class iterator to iterate over every DIF, False if you want it to
        iterate only over the sub-detectors.
        """
        self._iterate_by_dif = iterate_by_dif
        if self._iterate_by_dif:
            self.wallmrd_north_top = State("WallMRD north top", True, True)
            self.wallmrd_north_bottom = State("WallMRD north bottom", True, True)
            self.wallmrd_south_top = State("WallMRD south top", True, True)
            self.wallmrd_south_bottom = State("WallMRD south bottom", True, True)
            self.wagasci_upstream_top = State("WAGASCI upstream top", True, True)
            self.wagasci_upstream_side = State("WAGASCI upstream side", True, True)
            self.wagasci_downstream_top = State("WAGASCI downstream top", True, True)
            self.wagasci_downstream_side = State("WAGASCI downstream side", True, True)
        else:
            self.wallmrd_north = State("WallMRD north", True, False)
            self.wallmrd_south = State("WallMRD south", True, False)
            self.wagasci_upstream = State("WAGASCI upstream", True, False)
            self.wagasci_downstream = State("WAGASCI downstream", True, False)

    @property
    def iterate_by_dif(self):
        """
        :return: True if the class iterator is iterating over all the DIFs, False if it is iterating only over the
        whole subdetectors.
        """
        return self._iterate_by_dif

    def import_topology(self, topology):
        # type: (Topology) -> None
        """
        Copy the topology object, while preserving its own iteration mode. The iteration mode of the other Topology
        object might be different.
        :param topology: other Topology object
        :return: None
        """
        if self.iterate_by_dif and not topology.iterate_by_dif:
            if topology.wagasci_upstream.is_enabled():
                self.wagasci_upstream_top.enable()
                self.wagasci_upstream_side.enable()
            else:
                self.wagasci_upstream_top.disable()
                self.wagasci_upstream_side.disable()
            if topology.wagasci_downstream.is_enabled():
                self.wagasci_downstream_top.enable()
                self.wagasci_downstream_side.enable()
            else:
                self.wagasci_downstream_top.disable()
                self.wagasci_downstream_side.disable()
            if topology.wallmrd_north.is_enabled():
                self.wallmrd_north_top.enable()
                self.wallmrd_north_bottom.enable()
            else:
                self.wallmrd_north_top.disable()
                self.wallmrd_north_bottom.disable()
            if topology.wallmrd_south.is_enabled():
                self.wallmrd_south_top.enable()
                self.wallmrd_south_bottom.enable()
            else:
                self.wallmrd_south_top.disable()
                self.wallmrd_south_bottom.disable()
        elif not self.iterate_by_dif and topology.iterate_by_dif:
            if topology.wagasci_upstream_top.is_enabled() or topology.wagasci_upstream_side.is_enabled():
                self.wagasci_upstream.enable()
            else:
                self.wagasci_upstream.disable()
            if topology.wagasci_downstream_top.is_enabled() or topology.wagasci_downstream_side.is_enabled():
                self.wagasci_downstream.enable()
            else:
                self.wagasci_downstream.disable()
            if topology.wallmrd_north_top.is_enabled() or topology.wallmrd_north_bottom.is_enabled():
                self.wallmrd_north.enable()
            else:
                self.wallmrd_north.disable()
            if topology.wallmrd_south_top.is_enabled() or topology.wallmrd_south_bottom.is_enabled():
                self.wallmrd_south.enable()
            else:
                self.wallmrd_south.disable()
        else:
            for key, value in vars(self).items():
                setattr(self, key, getattr(topology, key))

    def are_all_enabled(self):
        # type: (...) -> bool
        """
        :return: True if all DIFs are enabled
        """
        for value in vars(self).values():
            if isinstance(value, State) and value.is_enabled() is False:
                return False
        return True

    def disable_all_but(self, one):
        # type: (str) -> None
        """
        Disable all the subdetectors or DIFs but the one with the specified name
        :param one: subdetector or DIF not to disable
        :return: None
        """
        for d in vars(self).values():
            if isinstance(d, State):
                if d.name == one:
                    d.enable()
                else:
                    d.disable()

    def how_many_enabled(self):
        # type: (...) -> int
        """
        :return: how many subdetectors or DIFs are enabled
        """
        return len(self.get_enabled())

    def disable_all(self):
        # type: (...) -> None
        """
        Disable everything
        :return: None
        """
        for d in vars(self).values():
            if isinstance(d, State):
                d.disable()

    def get_all(self):
        # type: (...) -> List[State]
        """
        :return: list of all the subdetectors or DIFs states (as objects of class State)
        """
        if self._iterate_by_dif:
            return [value for value in vars(self).values() if isinstance(value, State) and value.is_dif() is True]
        else:
            return [value for value in vars(self).values() if isinstance(value, State) and value.is_dif() is False]

    def get_enabled(self):
        # type: (...) -> List[State]
        """
        :return: list of enabled subdetectors or DIFs states (as objects of class State)
        """
        if self._iterate_by_dif:
            return [value for value in vars(self).values()
                    if isinstance(value, State) and value.is_dif() is True and value.is_enabled() is True]
        else:
            return [value for value in vars(self).values()
                    if isinstance(value, State) and value.is_dif() is False and value.is_enabled() is True]

    def get_disabled(self):
        # type: (...) -> List[State]
        """
        :return: list of disabled subdetectors or DIFs states (as objects of class State)
        """
        if self._iterate_by_dif:
            return [value for value in vars(self).values()
                    if isinstance(value, State) and value.is_dif() is True and value.is_enabled() is False]
        else:
            return [value for value in vars(self).values()
                    if isinstance(value, State) and value.is_dif() is False and value.is_enabled() is False]

    def __iter__(self):
        # type: (...) -> TopologyIterator
        """
        Returns a TopologyIterator object (an iterator over the Topology class). The iterator iterates over the DIFs
        or over the sub-detectors depending on the iterator mode set through the iterate_by_dif constructor argument.
        :return: TopologyIterator object
        """
        return TopologyIterator(self)


class TopologyIterator(object):
    """
    Iterator over the Topology class
    """
    def __init__(self, topology):
        # type: (Topology) -> None
        """
        :param topology: Topology object which to iterate over
        """
        # Difs object reference
        self._topology = topology
        # member variable to keep track of current index
        self._index = 0

    def __next__(self):
        # type: (...) -> State
        """
        :return: next DIF or subdetector
        """
        if self._topology.iterate_by_dif:
            if self._index == int(DifIndex.WallMrdNorthTop):
                result = self._topology.wallmrd_north_top
            elif self._index == int(DifIndex.WallMrdNorthBottom):
                result = self._topology.wallmrd_north_bottom
            elif self._index == int(DifIndex.WallMrdSouthTop):
                result = self._topology.wallmrd_south_top
            elif self._index == int(DifIndex.WallMrdSouthBottom):
                result = self._topology.wallmrd_south_bottom
            elif self._index == int(DifIndex.WagasciUpstreamTop):
                result = self._topology.wagasci_upstream_top
            elif self._index == int(DifIndex.WagasciUpstreamBottom):
                result = self._topology.wagasci_upstream_side
            elif self._index == int(DifIndex.WagasciDownstreamTop):
                result = self._topology.wagasci_downstream_top
            elif self._index == int(DifIndex.WagasciDownstreamBottom):
                result = self._topology.wagasci_downstream_side
            else:
                raise StopIteration
        else:
            if self._index == DetectorIndex.WallMrdNorth:
                result = self._topology.wallmrd_north
            elif self._index == DetectorIndex.WallMrdSouth:
                result = self._topology.wallmrd_south
            elif self._index == DetectorIndex.WagasciUpstream:
                result = self._topology.wagasci_upstream
            elif self._index == DetectorIndex.WagasciDownstream:
                result = self._topology.wagasci_downstream
            else:
                raise StopIteration
        self._index += 1
        return result
