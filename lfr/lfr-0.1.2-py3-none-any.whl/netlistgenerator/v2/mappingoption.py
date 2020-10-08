from typing import List
from pymint.mintcomponent import MINTComponent
from pymint.mintdevice import MINTDevice


class WhereToConnectObject():

    def __init__(self) -> None:
        # This the parameter where you would have the LFR flow name
        self._id = ""
        self._is_netlist: bool = False
        self._component_name: str = ""
        self._component_port: int = -1


class MappingOption():

    def __init__(self) -> None:
        self.netlist: MINTDevice = None

        # This is the parameter that lets you check
        # if its a stroage type or not
        self._is_storage: bool = False

        # This is the paramemeter that lets you check
        # if the storage has inbuilt control elements or not
        self._has_storage_control: bool = False

        self._input_flows = []
        self._output_flows = []
        self._waste_flows = []

    def init_single_component(self, component: MINTComponent) -> None:
        if self.netlist is not None:
            raise Exception("Mapping Option already instantiated")
        else:
            self.netlist = MINTDevice("{}_only_netlist".format(component.name))

    def add_input_flow(self, where_to_connect: WhereToConnectObject) -> None:
        self._input_flows.append(where_to_connect)

    def add_output_flow(self, where_to_connect: WhereToConnectObject) -> None:
        self._input_flows.append(where_to_connect)

    def add_loading_flow(self, where_to_connect: WhereToConnectObject) -> None:
        self._input_flows.append(where_to_connect)
    
    def add_carrier_flow(self, where_to_connect: WhereToConnectObject) -> None:
        self._input_flows.append(where_to_connect)

    @property
    def is_storage(self):
        return self._is_storage

    @property
    def has_storage_control(self):
        return self._has_storage_control


class MappingOptionWithStorage():

    def __init__(self) -> None:
        super().__init__()
        self._is_storage = True
        self._load_flows = []
        self._carrier_flows = []
