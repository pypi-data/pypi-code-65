from lfr.netlistgenerator.v2.mappingoption import MappingOption
from typing import List
from lfr.netlistgenerator.explicitmapping import ExplicitMapping
from pymint.mintdevice import MINTDevice
from networkx import nx


class ConstructionNode():

    def __init__(self, node_id: str) -> None:
        self.id = node_id
        self.netlist: MINTDevice = MINTDevice(node_id)
        self.fig_subgraph: nx.DiGraph = None
        self._mapping_options: List[MappingOption] = []

    @property
    def id(self) -> str:
        return self.id

    def add_subgraph(self, subgraph) -> None:
        self.fig_subgraph = subgraph

    def attach_full_netlist(self, netlist: MINTDevice) -> None:
        self.netlist = netlist

    def use_explicit_mapping(self, mapping: ExplicitMapping) -> None:
        # Delete all the existing mapping options
        self._mapping_options.clear()
        # TODO -  Overwrite all the netlist options here
        # Go over the library to find all the mapping options
        # when you find the options get the corresponding mapping option
        pass
