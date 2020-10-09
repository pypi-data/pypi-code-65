#!/usr/bin/python
# coding: utf-8

import os
import subprocess as sp
import shutil
import datetime
import pickle
import distutils.util
import solid as s
import warnings
from typing import Dict, List, Tuple, Union, Optional

from .log import MyLog
from .object import ObjectCAD
from .reactor import ReactorCAD
from .flow_reactor import FlowReactorCAD
from .filter_like_reactors import FilterLikeReactor
from .connector import ConnectorCAD
from . import app_constants
from .exceptions import *
from .in_out import InputOutput


class Assembly(ObjectCAD):

    """
    Assembly class. Will store modules, and will handle tasks like arrangement
    of the modules (zigzag, line, etc) and finding optimal z for filters to
    minimize the number of pauses during 3D printing. Also generates previews
    for the assembly, and STLs for the modules (separate STLs or merged one)
    """

    # Background color of images generated with OpenSCAD. Can change
    # depending on the colorscheme
    BG_COLOR = "#F8F8F8"

    # Size for main preview (Openscad CLI params)
    IMG_SIZE_MAIN = "1000,1000"

    # Size for view (left, right, etc) (Openscad CLI params)
    IMG_SIZE = "3000,3000"

    DISTANCE = 1000

    def __init__(
        self,
        turn_x: int = 2,
        turn_y: int = 2,
        renders_dir: str = None,
        logger=None,
        *args,
        **kwargs,
    ) -> None:

        """
        Args:
            turn_x (int): nbr of modules in x before turning
            turn_y (int): nbr of modules in y before turning
            renders_dir (str): directory for rendered files
            logger: logger to log waht Assembly does
            *args:
            **kwargs:

        Returns:
            None
        """

        # Assign renders dir if not given as parameter
        if renders_dir is None:
            self.renders_dir = "."
        else:
            # Crash if renders_dir doesn't exist
            if not os.path.exists(renders_dir):
                raise FileNotFoundError("renders_dir is not a valid directory")
            self.renders_dir = renders_dir

        # Create logger
        if logger is None:
            self.l = MyLog("activity.log")
        else:
            self.l = logger

        self.l.debug(f"assembly renders_dir: {self.renders_dir}")

        # Get OpenSCAD path (the binaries are included with the lib),
        # OS dependent
        self.openscad_path: str = self._getOpenscadPath()

        self.l.debug(f"assembly openscad path: {self.openscad_path}")

        self.l.debug(f"assembly, turn_x: {turn_x}; turn_y: {turn_y}")

        self.turn_x: int = turn_x
        self.turn_y: int = turn_y

        self.linear = False

        self.counter_reactor: int = 0
        self.counter_connector: int = 0

        self._handleExtraArgs(kwargs)

        # List to store the reactor-like modules
        self.list_reactors: List[ReactorCAD] = list()

        # List to store the connector modules
        self.list_connectors: List[ConnectorCAD] = list()

        # List to store tuples of tops to be aligned
        self.list_align_tops: List[Tuple] = list()

        # List to store tuples of filters to be aligned
        self.list_align_filters: List[Tuple] = list()

        # dict view: camera parameters, for the preview rendering
        self.scad_params: Dict[str, str] = {
            "left": f"--camera=0,0,0,90,0,-90,{self.DISTANCE}",
            "right": f"--camera=0,0,0,90,0,90,{self.DISTANCE}",
            "top": f"--camera=0,0,0,0,0,0,{self.DISTANCE}",
            "bottom": f"--camera=0,0,0,180,0,0,{self.DISTANCE}",
            "front": f"--camera=0,0,0,90,0,0,{self.DISTANCE}",
            "rear": f"--camera=0,0,0,90,0,180,{self.DISTANCE}",
        }

    def toggleLinearAssembly(self):
        #Toggle the linear assembly
        self.linear = not self.linear
        if self.linear:
            self.turn_x: int = 1
            self.turn_y: int = 1
        else:
            print('Changing back to default values == 2')
            self.turn_x: int = 2
            self.turn_y: int = 2
        self.refresh()

    def _handleExtraArgs(self, kwargs: dict) -> None:

        """
        Handles named extra arguments passed to the init function

        Arguments:
            kwargs (dict): dict of name paramaters

        Returns:
            None
        """

        # If automatic_angles is True, Assembly will find the angles when connecting
        # modules. Else, user will have to define them
        if "automatic_angles" in kwargs:
            self.automatic_angles = kwargs["automatic_angles"]

            if not self.automatic_angles:
                self.turn_x = 1
                self.turn_y = 1
                self.l.debug(f"assembly, disabling turn_x and turn_y")
        else:
            self.automatic_angles = True

    @property
    def reactors_names(self) -> Dict[str, ReactorCAD]:

        """
        Return a dict of names and reactors for reactor-like reactors in assembly
        (BUT NOT connectors). Names = internal_id if user didn't modify them

        Returns:
            dict[str, ReactorCAD]: ex: {"Reactor extraction": Reactor object}
        """

        reactors: Dict[str, ReactorCAD] = dict()

        for obj in self.list_reactors:
            reactors[f"{obj.module_name}"] = obj

        return reactors

    @property
    def reactors_internal_ids(self) -> Dict[str, ReactorCAD]:

        """
        Return a dict of id and reactors for reactor-like reactors in assembly
        (BUT NOT connectors). Names are short version
        (ex: R0)

        Args:

        Returns:
            dict[str, ReactorCAD]: {"Rn": Reactor object}
        """

        reactors: Dict[str, ReactorCAD] = dict()

        for obj in self.list_reactors:
            reactors[f"{obj.internal_id}"] = obj

        return reactors

    @property
    def connectors_names(self) -> Dict[str, ConnectorCAD]:

        """
        Return a dict of names and connectors for connectors in assembly (BUT NOT
        reactors)

        Args:

        Returns:
            dict[str, ConnectorCAD]: {"Siphon n": Connector object}
        """

        connectors: Dict[str, ConnectorCAD] = dict()

        for obj in self.list_connectors:
            connectors[f"{obj.module_name}"] = obj

        return connectors

    @property
    def connectors_internal_ids(self) -> Dict[str, ConnectorCAD]:

        """
        Return a dict of id and connectors for connectors in assembly (BUT NOT
        reactors). (ex: S0)

        Args:

        Returns:
            dict[str, ConnectorCAD]: {"Sn": Connector object}
        """

        connectors: Dict[str, ConnectorCAD] = dict()

        for obj in self.list_connectors:
            connectors[f"{obj.internal_id}"] = obj

        return connectors

    @property
    def inputs(self) -> Dict[str, InputOutput]:

        """
        Return a dict of names and inputs for available inputs (BUT NOT
        external ones)

        Returns:
            Dict[str, InputOutput]
        """

        inputs: Dict[str, InputOutput] = dict()

        for obj in self.list_reactors:

            for name_io in obj.inputs:
                io = obj.inputs[name_io]
                if not io.external:
                    inputs[f"Input '{name_io}' from {self._getModuleName(obj)}"] = io

        return inputs

    @property
    def outputs(self) -> Dict[str, InputOutput]:

        """
        Return a dict of names and outputs for available outputs (BUT NOT
        external ones)

        Returns:
            Dict[str, InputOutput]
        """

        outputs: Dict[str, InputOutput] = dict()

        for obj in self.list_reactors:

            for name_io in obj.outputs:
                io = obj.outputs[name_io]
                if not io.external:
                    outputs[f"Output '{name_io}' from {self._getModuleName(obj)}"] = io

        return outputs

    def _getOpenscadPath(self) -> str:

        """
        Get OpenSCAD's path depending on the OS

        Returns:
            str: a path to openscad bin
        """

        platform = distutils.util.get_platform()

        self.l.debug(f"getOpenscadPath, platform: {platform}")

        if platform == "win-amd64" or platform == "win32":
            cur_path = os.path.dirname(os.path.abspath(__file__))
            openscad_path = os.path.join(cur_path, "bin", "win", "openscad.com")
            if platform == "win32":
                warnings.warn("You're running Windows 32bits. Might cause problems")
        elif platform == "linux-x86_64":
            openscad_path = "openscad"
        elif platform == "macosx" or platform == "macosx-10.9-x86_64" in platform:
            openscad_path = "openscad"
            #raise NotImplementedError("ChemCAD is not compatible with Mac OS (yet?)")
        return openscad_path

    def _findAngles(self) -> List[float]:

        """
        Find the angle of the default output for all the reactor-like
        objects in the assembly

        Returns:
            List[float] -- list of angles, for default outputs in assembly
        """

        # If turn_x or turn_y == 1, then the user doesn't want a zigzag pattern
        # Make the assembly as a straight sequence of reactors
        if self.turn_x == 1 or self.turn_y == 1:
            return [0 for i in self.list_reactors]

        # Generate a list of indexes for all the reactors in the assembly
        sample = [i for i in range(len(self.list_reactors))]

        # Find all the reactors involved in a turn
        turns_y: List[list] = list()
        while sample:
            sub_y = sample[self.turn_x - 1 : self.turn_x + self.turn_y - 1]
            turns_y.append(sub_y)
            sample = sample[self.turn_x + self.turn_y - 2 :]

        # Create two lists:
        # - one for reactors turning 90°
        # - one for reactors turning -90°
        list_90: List[int] = list()
        list_minus_90: List[int] = list()

        # Add each reactor index involved in a turn to the proper list of
        # angles
        for i, values in enumerate(turns_y):
            if i % 2 == 0:
                for e in values:
                    # Only first and last reactor or involved in a turn, others
                    # are straight
                    if e is values[0] or e is values[-1]:
                        list_minus_90.append(e)
            else:
                for e in values:
                    if e is values[0] or e is values[-1]:
                        list_90.append(e)

        angles: List[int] = list()

        # For all the reactors in the assembly, find the angle
        for index, reactor in enumerate(self.list_reactors):

            # Find in which list the new reactor is and return
            # appropriate angle
            if index in list_90:
                angles.append(90)
            elif index in list_minus_90:
                angles.append(-90)
            else:
                angles.append(0)

        return angles

    def _alignFilters(
        self, mod_moving: FilterLikeReactor, mod_target: FilterLikeReactor
    ) -> None:

        """
        Will align the filter of mod_moving to the filter of mod_target.
        Delegate how the filter should be aligned to the module.

        Args:
            mod_moving (FilterLikeReactor): module with filter to align on target
            mod_target (FilterLikeReactor): module with target filter to align on

        Returns:
            None
        """

        # If exception raised, one module has no filter, exit
        try:
            _ = mod_moving.z_top_filter
            target_height = mod_target.z_top_filter
        except AttributeError as e:
            self.l.error(f"{e}: one of the module has no filter", exc_info=True)
            return

        mod_moving.alignFilterToHeight(target_height)

    def _alignTops(self, mod_moving: ReactorCAD, mod_target: ReactorCAD) -> None:

        """
        Will align the top of mod_moving on the top of mod_target. The top
        being the top of the module WITHOUT outlets.
        Use 'lift' or 'expand' strategies.

        Args:
            mod_moving (ReactorCAD): module with moving top
            mod_target (ReactorCAD): module with target top

        Returns:
            None
        """

        # TODO: completely untested, so test this function

        height_moving: float = mod_moving.infos["height_wo_inlet"]
        height_target: float = mod_target.infos["height_wo_inlet"]

        grow = height_target - height_moving

        if grow == 0:
            return

        # Lift strategy, but target filter is lower than moving filter, crash
        if mod_moving.align_top_strategy == "lift" and grow < 0:
            mes = "The target top is lower than the moving top, can't lift"
            raise ImpossibleAction(mes)

        # Lift strategy, moving filter lower than target filter, all good
        elif mod_moving.align_top_strategy == "lift" and grow > 0:
            mod_moving.liftReactor(grow)

        # Expand strategy, use the module's expand strategy (several
        # different expand strategies for FFR for example)
        elif mod_moving.align_top_strategy == "expand":
            mod_moving.expandVertically(grow)

        mod_moving.top_aligned = True

    def removeCoupleAlignTops(self, couple: Tuple[ReactorCAD, ReactorCAD]) -> None:

        """
        Remove a couple of modules to the list of tops to align

        Args:
            couple (Tuple[ReactorCAD, ReactorCAD]): (module moving, module target)

        Returns:
            None
        """

        mod_mov, _ = couple

        mod_mov.top_aligned = False

        self.list_align_tops.remove(couple)

    def cleanAlignTops(self) -> None:

        """Clean the list of tops to align. Utility function for user"""

        self.list_align_tops.clear()

    def cleanAlignFilters(self) -> None:

        """Clean the list of filters to align. Utility function for user"""

        self.list_align_filters.clear()

    def removeCoupleAlignFilters(self, couple: tuple) -> None:

        """Remove a couple of modules to the list of filters to align"""

        self.list_align_tops.remove(couple)

    def _findFirstReactorInChain(self) -> ReactorCAD:

        """
        Find the first reactor in the reactor chain. i.e. the only reactor with a
        connected, internal output, and no internal input

        Returns:
            ReactorCAD: First reactor in reactor chain.
        """

        for reactor in self.list_reactors:
            if (
                not reactor.hasConnectedInternalInput()
                and reactor.hasInternalConnectedOutput()
            ):
                return reactor

    def _findNextConnector(self, reactor: ReactorCAD) -> Optional[ConnectorCAD]:

        """
        Find next connector connected to given reactor

        Arguments:
            reactor (ReactorCAD): Reactor connector is connected to.

        Returns:
            Optional[ConnectorCAD]: Connector attached to given reactor
        """

        for connector in self.list_connectors:
            if connector.obj_in is reactor:
                return connector

        return None

    def _reorderConnectors(self) -> None:

        """
        Reorder connectors so that they are in the order of the reactor chain.

        Returns:
            None
        """

        # If less than 2 connectors in assembly, no need to reorder
        if len(self.list_connectors) < 2:
            return

        ordered_list_connectors: List[ConnectorCAD] = list()

        chain_start_reactor = self._findFirstReactorInChain()

        next_connector = self._findNextConnector(chain_start_reactor)

        while next_connector is not None:
            ordered_list_connectors.append(next_connector)
            next_connector = self._findNextConnector(next_connector.obj_out)

        self.list_connectors = ordered_list_connectors

    def _objMustBeRendered(self, obj: ObjectCAD) -> bool:

        """
        Check if module must be rendered. Module not rendered if not connected,
        except if only reactor of assembly, or first reactor in assembly

        Args:
            obj (ObjectCAD): the CAD object being tested for rendering

        Returns:
            bool: True if obj must be rendered, False otherwise
        """

        # If only one reactor in assembly, obj must be rendered.
        # If several objects in assembly and obj is first reactor in assembly,
        # obj must be rendered
        if len(self.list_reactors) == 1 or obj is self.list_reactors[0]:
            return True
        else:
            if not obj.isConnected():
                return False
            else:
                return True

    def _objHasChanged(self, obj: ObjectCAD) -> bool:

        """
        Check if module has changed (check if cad code is same as code stored in
        scad file)

        Args:
            obj (ObjectCAD): the CAD object being tested for changes

        Returns:
            bool: True ig obj has changed, False otherwise
        """

        scad_file = os.path.join(self.renders_dir, f"{self._getModuleID(obj)}.scad")

        # Get the code in the SCAD file
        with open(scad_file, "r") as comp_f:
            cad_code = comp_f.read()

        # If the code in the SCAD file is different from the actual
        # code of the object, then the object was modified
        return cad_code != obj.code

    def _objIsNew(self, obj: ObjectCAD) -> bool:

        """
        Check if a module is new (newly created, soon-to-be rendered).
        If it's new, there is no corresponding scad file in the render dir.

        Args:
            obj (ObjectCAD): the obj being tested

        Returns:
            bool: True if obj is new, False otherwise
        """

        scad_file = os.path.join(self.renders_dir, f"{self._getModuleID(obj)}.scad")

        return not os.path.exists(scad_file)

    def _getModuleName(self, obj: ObjectCAD) -> str:

        """
        Get the name of the module obj

        Args:
            obj (ObjectCAD): the module with the name to be found

        Returns:
            str: the name of the module. Ex: "R0", or "Reactor extraction"
        """

        for name, reactor in self.reactors_names.items():
            if obj is reactor:
                return name

        for name, connector in self.connectors_names.items():
            if obj is connector:
                return name

    def _getModuleID(self, obj: ObjectCAD) -> str:

        """
        Get the ID of the module obj

        Args:
            obj (ObjectCAD): the module with the ID to be found

        Returns:
            str: the ID of the module. Ex: R0
        """

        for internal_id, reactor in self.reactors_internal_ids.items():
            if obj is reactor:
                return internal_id

        for internal_id, connector in self.connectors_internal_ids.items():
            if obj is connector:
                return internal_id

    def getModuleIDFromName(self, module_name: str) -> str:

        """
        Get a module's ID from its name

        Arguments:
            module_name (str): The module name

        Returns:
            str: Module's ID
        """

        if module_name in self.reactors_names:
            obj = self.reactors_names[module_name]
        else:
            obj = self.connectors_names[module_name]

        return self._getModuleID(obj)

    def addAlignTops(self, mod_moving: ReactorCAD, mod_target: ReactorCAD) -> None:

        """
        Will align the top of mod_moving to the top of mod_target. The top being
        the top of the module WITHOUT outlets.

        Args:
            mod_moving (ReactorCAD): align the top of this module
            mod_target (ReactorCAD): target top to align on

        Returns:
            None
        """

        self.list_align_tops.append((mod_moving, mod_target))

    def addAlignFilters(self, mod_moving: ReactorCAD, mod_target: ReactorCAD) -> None:

        """
        Will align the filter of mod_moving to the filter of mod_target.
        Align the top of the filters

        Args:
            mod_moving (ReactorCAD): align the filter of this module
            mod_target (ReactorCAD): target filter to align on

        Returns:
            None
        """

        self.list_align_filters.append((mod_moving, mod_target))

    def appendModule(self, module: Union[ReactorCAD, ConnectorCAD]) -> None:

        """
        Append a module to the assembly. if the module is instance of ReactorCAD,
        put it in the list_reactors list. If the module is instance of ConnectorCAD,
        put it in list_connectors.

        Args:
            module (Union[ReactorCAD, ConnectorCAD]): module to append to the assembly

        Returns:
            None
        """

        # If object is reactor, put it in list_reactors
        if isinstance(module, ReactorCAD) or isinstance(module, FlowReactorCAD):
            self.l.debug("Adding new module to assembly")
            self.list_reactors.append(module)

            # Initialize the internal id of the module
            # Initialize module's name
            self.counter_reactor += 1
            module.internal_id = f"{module.module_type_short}{self.counter_reactor}"
            module.module_name = f"{module.module_type_short}{self.counter_reactor}"

        # If object is connector, put it in list_connectors
        elif isinstance(module, ConnectorCAD):
            self.l.debug("Adding new connector to assembly")
            self.list_connectors.append(module)

            self.counter_connector += 1
            module.internal_id = f"{module.module_type_short}{self.counter_connector}"
            module.module_name = f"{module.module_type_short}{self.counter_connector}"

    def deleteModule(self, module: Union[ReactorCAD, ConnectorCAD]) -> None:

        """
        Delete a module from assembly. if the module is instance of ReactorCAD,
        remove it from list_reactors list. If the module is instance of ConnectorCAD,
        remove it from list_connectors.

        JP added 1 to a counter every time a module was added. It would make sense
        to substract 1 now, but he is using that counter for naming stuff, therefore
        if we substract 1 we risk that new objects might have the same name. Thus
        I have decided not to substract anything from the counter when an element
        is removed. Hopefully in his code he only uses this counter for naming.

        Args:
            module (Union[ReactorCAD, ConnectorCAD]): module to remove from the assembly

        Returns:
            None
        """

        # First remove scad and stl files
        module_internal_id = self._getModuleID(module)
        self.removeSCADandSTL(module_internal_id)

        # If object is reactor, remove it from list_reactors
        if isinstance(module, ReactorCAD):
            self.l.debug("Removing reactor from assembly")
            self.list_reactors.remove(module)

            # We also need to remove all the connectors connected
            # to it because JP doesnt let exist unconnected
            # connectors
            for name, inp in module.inputs.items():
                if inp.connected:
                    con_module = inp.connectedTo
                    self.deleteModule(con_module)

            for name, output in module.outputs.items():
                if output.connected:
                    con_module = output.connectedTo
                    self.deleteModule(con_module)

        # If object is connector, remove it from list_connectors
        elif isinstance(module, ConnectorCAD):
            self.l.debug("Removing connector from assembly")
            self.list_connectors.remove(module)

            # and disconnect its input/outputs
            module.in_io = None
            module.out_io = None

    def removeSCADandSTL(self, name: str) -> None:

        """
        Deletes the files name.scad and name.stl from the renders folder

        Args:
            name (str): name of the files to remove

        Returns:
            None
        """

        scad_file = os.path.join(self.renders_dir, name+".scad")
        stl_file = scad_file+".stl"

        try:
            os.remove(scad_file)
            self.l.debug(f"removeSCADandSTL, removing {scad_file}")
        except FileNotFoundError:
            pass

        try:
            os.remove(stl_file)
            self.l.debug(f"removeSCADandSTL, removing {stl_file}")
        except FileNotFoundError:
            pass

    def refresh(self) -> None:

        """
        Refresh the assembly. Triggered by the GUI when a module/connector was
        modified. Will reset reactors' transformations. Will then align tops,
        align filters, and refresh all the connectors. The reactors will finally be
        translated/rotated to their new/right position.
        """

        self.l.debug("Starting assembly refresh")

        self._resetReactors()

        if self.automatic_angles:

            # Get def_out_angle for all reactors in assembly
            angles = self._findAngles()
            self.l.debug(f"Assembly automatic angles: {angles}")

            for reactor, angle in zip(self.list_reactors, angles):

                # Set def_out_angle for reactor
                try:
                    reactor.def_out_angle = angle
                except KeyError:
                    self.l.debug("refresh: no default output for reactor, passing")

        # Align tops that need to be aligned
        for couple in self.list_align_tops:
            self._alignTops(*couple)

        # Align filters that need to be aligned
        for couple in self.list_align_filters:
            self._alignFilters(*couple)

        self._reorderConnectors()

        # Refresh all connectors, all modules should be properly translated
        for con in self.list_connectors:
            con.refresh()

        self.l.debug("Assembly refresh finished")

    def _resetReactors(self) -> None:

        """
        Reset reactors' positions and rotation angles, and z offset

        Returns:
            None
        """

        for reactor in self.list_reactors:
            # Reset position of reactor in assembly
            reactor.coo["x"] = 0
            reactor.coo["y"] = 0

            old_z = reactor.coo["z"]
            reactor.coo["z"] = 0

            # Get old angle of reactor
            old_angle = reactor.coo["angle"]

            # Cancel rotation of reactor
            reactor.coo["angle"] -= old_angle

            # Cancel rotation for all inputs
            # Cancel z translation for all inputs
            for in_io in reactor.inputs.values():
                in_io.height -= old_z
                in_io.angle -= old_angle

            # Cancel rotation for all outputs
            # Cancel z translation for all outputs
            for name, out_io in reactor.outputs.items():
                out_io.height -= old_z
                out_io.angle -= old_angle

    def prepareRenderSTLs(self) -> None:

        """
        Will generate a .scad file for each module and connector of the
        assembly

        Returns:
            None
        """

        list_modules: Union[
            List[ReactorCAD], List[ConnectorCAD]
        ] = self.list_reactors + self.list_connectors

        # For each CAD object
        for obj in list_modules:

            module_internal_id = self._getModuleID(obj)

            # If module needs to be rendered (doesn't render unconnected
            # object for example)
            if self._objMustBeRendered(obj):

                # If module is new, render
                if self._objIsNew(obj):

                    self.l.debug(f"{module_internal_id} is new, preparing scad file")

                    scad_file = os.path.join(
                        self.renders_dir, f"{module_internal_id}_to_render.scad"
                    )
                    obj.renderToFile(scad_file)

                # If module changed, remove old file, re-render
                elif self._objHasChanged(obj):

                    self.l.debug(f"{module_internal_id} changed, scad file regenerated")

                    # Remove old scad file
                    old_file = os.path.join(
                        self.renders_dir, f"{module_internal_id}.scad"
                    )
                    os.remove(old_file)

                    scad_file = os.path.join(
                        self.renders_dir, f"{module_internal_id}_to_render.scad"
                    )
                    obj.renderToFile(scad_file)

            # If module must not be rendered, try to remove old scad file
            else:
                # Remove old scad file
                old_file = os.path.join(self.renders_dir, f"{module_internal_id}.scad")
                try:
                    os.remove(old_file)
                    self.l.debug(f"prepareRenderSTLs, removing {old_file}")
                except FileNotFoundError:
                    pass
                # Remove old stl file
                old_file = os.path.join(self.renders_dir, f"{module_internal_id}.scad.stl")
                try:
                    os.remove(old_file)
                    self.l.debug(f"prepareRenderSTLs, removing {old_file}")
                except FileNotFoundError:
                    pass
    def switchToUHD(self) -> None:

        """
        Increase fn for each module in assembly. All modules will be rendered
        in UHD

        Returns:
            None
        """

        # TODO: get custom fn and fs value, for each type of module

        self.l.debug("Switching assembly to ULTRA high definition")

        list_modules: Union[
            List[ReactorCAD], List[ConnectorCAD]
        ] = self.list_reactors + self.list_connectors

        for obj in list_modules:
            obj.fn = 200

    def switchToHD(self) -> None:

        """
        Increase fn for each module in assembly. All modules will be rendered
        in HD

        Returns:
            None
        """

        # TODO: get custom fn and fs value, for each type of module

        self.l.debug("Switching assembly to high definition")

        list_modules: Union[
            List[ReactorCAD], List[ConnectorCAD]
        ] = self.list_reactors + self.list_connectors

        for obj in list_modules:
            obj.fn = 75

    def switchToLD(self) -> None:

        """
        Decrease fn for each module in assembly. All modules will be rendered
        in low definition

        Returns:
            None
        """

        self.l.debug("Switching assembly to low definition")

        list_modules: Union[
            List[ReactorCAD], List[ConnectorCAD]
        ] = self.list_reactors + self.list_connectors

        for obj in list_modules:
            obj.fn = app_constants.fn
            obj.fs = app_constants.fs

    def _buildCadCode(self) -> s.objects.union:

        """
        Build the CAD code w/ SolidPython.
        Get the cad code of every object in the assembly and merge them

        Raises:
            ValueError: when a connector is missing in the assembly

        Returns:
            s.objects.union: the CAD object for the entire assembly
        """

        list_modules: Union[
            List[ReactorCAD], List[ConnectorCAD]
        ] = self.list_reactors + self.list_connectors

        if len(self.list_reactors) - 1 != len(self.list_connectors):
            raise ValueError("Missing connectors in assembly")

        total = self.list_reactors[0].cad

        for cad_obj in list_modules[1:]:
            total += cad_obj.cad

        return total

    def renderToFile(self, file_path: str) -> None:

        """
        Subclass ObjectCAD renderToFile method to render the scad file
        in renders_dir

        Arguments:
            file_path (str): the destination path for the scad file

        Returns:
            None
        """

        # Forge path
        file_path = os.path.join(self.renders_dir, file_path)

        super().renderToFile(file_path)

    def renderSTL(self, file_name: str) -> None:

        """
        Will render the file 'file_name' to a STL file. Mainly called from
        GUI in a thread. 'file_name' is supposed to be the stl file for
        one module of an assembly

        Arguments:
            file_name (str): the name of the scad file to be rendered

        Raises:
            FileNotFoundError: when the scad file to be rendered can't be found

        Returns:
            None
        """

        # Forge path for scad file
        scad_file = os.path.join(self.renders_dir, file_name)

        # Check the path for the scad file exists
        if not os.path.exists(scad_file):
            raise FileNotFoundError(f"{scad_file} does not exist")

        # Forge the path of the STL file
        new_file_name = file_name.replace("_to_render", "")
        path_stl = os.path.join(self.renders_dir, f"{new_file_name}.stl")

        self.l.debug(f"Starting rendering {new_file_name}.stl")

        # Start a timer
        start_time = datetime.datetime.now()

        # Generate STL with OpenSCAD
        cmd = sp.Popen(
            [self.openscad_path, "-o", path_stl, scad_file],
            stdout=sp.PIPE,
            stderr=sp.PIPE,
        )

        # Wait until rendering is finished
        out, err = cmd.communicate()

        # Check if command succeeded
        if cmd.returncode != 0:
            self.l.error(
                f"Failed to generate stl for file {file_name}.scad. Error {cmd.returncode}"
            )
            return

        new_scad_file = os.path.join(self.renders_dir, new_file_name)

        # Rename the _to_render.scad file, rendering just happened
        os.rename(scad_file, new_scad_file)

        self.l.debug(
            f"{file_name}.stl rendered in {datetime.datetime.now() - start_time}"
        )

    def exportAssemblyToDict(self) -> Dict[str, Union[int, list]]:

        """
        Return a dict to store Assembly's attributes. Attributes' names are the key
        of the dict, the values are the attributes. Mainly used for saving Assembly
        objects.

        Ex: {"list_reactors": self.list_reactors}

        Returns:
            Dict[str, Union[int,list]]: {key, list of CAD object or int}
        """

        # Create a dict of all attributes to save
        dict_save: Dict[str, Union[int, list]] = dict()

        dict_save["turn_x"] = self.turn_x
        dict_save["turn_y"] = self.turn_y
        dict_save["list_reactors"] = self.list_reactors
        dict_save["list_connectors"] = self.list_connectors
        dict_save["list_align_tops"] = self.list_align_tops
        dict_save["list_align_filters"] = self.list_align_filters
        dict_save["counter_reactor"] = self.counter_reactor
        dict_save["counter_connector"] = self.counter_connector

        self.l.debug(f"assembly, exporting {dict_save}")

        return dict_save

    def saveProject(self, destination: str) -> None:

        """
        Save the project (current assembly) in a .ccad file

        Arguments:
            destination (str): destination path for ccad save file

        Returns:
            None
        """

        self.l.debug(f"assembly: saving project to {destination}")

        dict_save = self.exportAssemblyToDict()

        # Open the destination file and use pickle to dump the dict
        with open(destination, "wb") as f_out:
            pickle.dump(dict_save, f_out)

        self.l.debug(f"assembly: saved project to {destination}")

    def openProject(self, source: str) -> None:

        """openProject

        Open a project, a pickled assembly stored as a .ccad file.
        source is the path of the .ccad file

        Args:
            source (str): the path for the ccad save file to be open

        Returns:
            None
        """

        self.l.debug(f"assembly: opening {source}")

        try:
            # Unpickle the dict stored in the save file
            with open(source, "rb") as f_in:
                dict_restore = pickle.load(f_in)
        except FileNotFoundError:
            self.l.error(
                f"openProject: {repr(source)} not found, handled", exc_info=True
            )
            return

        # Restore the main attributes from the unpickled dict
        self.turn_x = dict_restore["turn_x"]
        self.turn_y = dict_restore["turn_y"]
        self.list_reactors = dict_restore["list_reactors"]
        self.list_connectors = dict_restore["list_connectors"]
        self.list_align_tops = dict_restore["list_align_tops"]
        self.list_align_filters = dict_restore["list_align_filters"]
        self.counter_reactor = dict_restore["counter_reactor"]
        self.counter_connector = dict_restore["counter_connector"]

        self.l.debug(f"assembly, opening: {dict_restore}")
        self.l.debug(f"assembly: {source} opened")

    def mergeSTLs(self, toIgnore:list = []) -> None:

        """
        Merge all the STLs in the renders dir into one
        https://stackoverflow.com/questions/13613336/python-concatenate-text-files

`       Args:
            toIgnore (list): List of meshes that the user clicked as visibility
            off. These meshes won't be rendered

        Returns:
            None
        """

        # Forge name for output stl
        output_stl = os.path.join(self.renders_dir, "final.stl")

        # Sort files based on their name. Ensure consistent tests
        list_entries = sorted(os.scandir(self.renders_dir), key=lambda e: e.name)

        with open(output_stl, "wb") as wfd:

            for entry in list_entries:

                # Pass all files 'final' in their name. Could be more specific and
                # pass 'final.stl', but I use a file final_test for the tests
                if "final" in entry.name:
                    continue

                if entry.name.endswith(".stl"):

                    if entry.name in toIgnore:
                        continue

                    with open(entry, "rb") as fd:
                        shutil.copyfileobj(fd, wfd, 1024 * 1024 * 10)


    def getPauses(self) -> List[float]:

        """getPauses

        Get the top height for each filter in the assembly, build a list
        and return it. Also display/log these heights

        Returns:
            List[float]
        """

        list_pauses = list()

        for r in self.list_reactors:
            height = getattr(r, "z_top_filter", None)

            if height is not None:
                list_pauses.append(height)
                self.l.info(f"Pause at {height} mm")

        return list_pauses


if __name__ == "__main__":

    from .reactor import ReactorCAD as rea
    from .filter_reactor import FilterReactorCAD as f_rea
    from .floating_filter_reactor import FloatingFilterReactorCAD as ff_rea
    from .siphon import SiphonCAD as siph
    from .double_siphon import DoubleSiphonCAD as d_siph
    from .tube_connector import TubeConnectorCAD as t_con
    import time

    # ass = Assembly(automatic_angles=False)
    ass = Assembly()

    # ass = Assembly(turn_x=2, turn_y=2)

    r_1 = rea(100, rea.T_OPEN, rea.B_ROUND_IN_O)
    ass.appendModule(r_1)

    ass.refresh()

    r_2 = rea(20, rea.T_OPEN, rea.B_ROUND_IN_O)
    r_2.addInputPercentage("test")
    ass.appendModule(r_2)

    ass.refresh()

    # con1 = t_con(r_1, r_1.outputs['default'], r_2, r_2.inputs['test'], conflicts="move_out_io")
    # con1 = t_con(r_1, r_1.outputs['default'], r_2, r_2.inputs['test'])
    # con1 = siph(r_1, r_1.outputs['default'], r_2, r_2.inputs['test'])
    con1 = d_siph(r_1, r_1.outputs["default"], r_2, r_2.inputs["test"])
    ass.appendModule(con1)

    ass.refresh()

    # ass.fn = 50

    # ass.getPauses()
    ass.saveProject("test.ccad")

    # ass.renderToFile("test2.scad")

    ass2 = Assembly()
    ass2.openProject("test.ccad")

    pass
