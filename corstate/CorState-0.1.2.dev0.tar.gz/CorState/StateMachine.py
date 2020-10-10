'''
File: StateMachine.py
Created Date: Thursday, July 4th 2020, 10:01:03 pm
Author: Zentetsu

----

Last Modified:
Modified By:

----

Project: CorState
Copyright (c) 2020 Zentetsu

----

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

----

HISTORY:
2020-10-10	Zen	Updating JSON file loading
2020-09-18	Zen	Using inf value for first and last transition
2020-09-17	Zen	Adding encapsulated state
2020-09-12	Zen	Updating init by JSON file
2020-09-12	Zen	Updating some comments
2020-09-10	Zen	Generating StateMachine from JSON file
2020-09-10	Zen	Refactoring the StateMachine structure
'''


import os
import json
from math import inf
from .State import State
from .Transition import Transition
from .CorStateError import *


class StateMachine:
    """StateMachine class
    """
    def __init__(self, name: str):
        """Class constructor
        """
        self._name = name
        self._states = {}
        self._transitions = {}
        self._states_stack = []

        self._data = None

    def getName(self) -> str:
        """Method that returns StateMachine name

        Returns:
            str: StateMachine name
        """
        return self._name

    def start(self):
        """Method that launches the state StateMachine
        """
        self._checkStateMachineIntegrity()

        _stateID = inf
        _breaked = True
        _next_transition = False

        while _breaked:
            _breaked = False

            for tr in self._transitions.keys():
                if self._transitions[tr].getInOutID()[0] == _stateID and self._transitions[tr].evaluate():
                    _stateID = self._transitions[tr].getInOutID()[1]

                    if len(self._states_stack) > 0 and -_stateID in self._states_stack:
                        while len(self._states_stack) > 0:
                            if self._states_stack[-1] != -_stateID:
                                del self._states_stack[-1]
                            else:
                                break

                        del self._states_stack[-1]
                        _next_transition = True

                    _breaked = True
                    break

            if _breaked and _stateID != -inf and not _next_transition:
                if self._states[_stateID].getEncapsulation():
                    self._states_stack.append(_stateID)

                self._states[_stateID].run()
            elif _next_transition:
                _next_transition = False

        if _stateID != -inf:
            print("ERROR")

    def addState(self, value=None, path:str=None):
        """Method that adds a state to the StateMachine

        Args:
            value ([type], optional): Value that will initialize a new State. Defaults to None.
            path (str, optional): Path to the called function for the StateMachine. Defaults to None.

        Raises:
            SMAddingStateError: raise an error when the value can't be casted into a State
        """
        if type(value) is dict:
            _state = State()
            _state.initBySFF(value, path)
        elif type(value) is State:
            _state = value
        elif value is None:
            _state = State()
            _state.addAction(value)
        else:
            raise SMAddingStateError

        self._states[_state.getID()] = _state

    def removeState(self, state_id:int):
        """Method which removes a state from the StateMachine

        Args:
            state_id (int): state id
        """
        del self._states[state_id]

    def getStates(self):
        """Method that returns States dict

        Returns:
            dict: States dict
        """
        return self._states

    def addTransition(self, value=None, path:str=None):
        """Method that adds a transition to the StateMachine

        Args:
            value ([type], optional): Value that will initialize a new Transition. Defaults to None.
            path (str, optional): Path to the called function for the StateMachine. Defaults to None.

        Raises:
            SMAddingStateError: raise an error when the value can't be casted into a Transition
        """
        if type(value) is dict:
            _transition = Transition()
            _transition.initByTFF(value, path)
        elif type(value) is Transition:
            _transition = value
        elif value is None:
            _transition = Transition()
            _transition.addEvaluation(value)
        else:
            raise SMAddingTransitionError

        self._transitions[_transition.getID()] = _transition

    def removeTransition(self, transition_id:int):
        """Method which removes a Transition from the Transition Machine

        Args:
            transition_id (int): Transition id
        """
        del self._transitions[transition_id]

    def getTransitions(self):
        """Method that returns Transitions dict

        Returns:
            [type]: Transition dict
        """
        return self._transitions

    def _checkStateMachineIntegrity(self):
        """Method that checks the integrity of the StateMachine
        """
        if [self._transitions[t].getInOutID()[0] == inf and self._transitions[t].getInOutID()[1] in self._states.keys() for t in self._transitions.keys()].count(True) != 1:
            raise SMIntegrityError("Initial")

        if [self._transitions[t].getInOutID()[1] == -inf and self._transitions[t].getInOutID()[0] in self._states.keys() for t in self._transitions.keys()].count(True) != 1:
            raise SMIntegrityError("Final")

    def _checkJSONIntegrity(self):
        """Method that checks the JSON file integrity

        Raises:
            SMJSONIntegrityError: raise an error when an element is not present into the JSON file
        """
        if not all([k in self._data.keys() for k in ["path", "StateMachine"]]):
            raise SMJSONIntegrityError("module_name, path and/or StateMachine values of JSON file")

        if not all([k in self._data["StateMachine"].keys() for k in ["Variable", "State", "Transition"]]):
            raise SMJSONIntegrityError("Variable, State and/or Transition values of StateMachine")

        if len(self._data["StateMachine"]["State"].keys()) > 0 and not all([k in self._data["StateMachine"]["State"][s].keys() for k in ["id", "action", "encapsulation"] for s in self._data["StateMachine"]["State"].keys()]):
            raise SMJSONIntegrityError("id and/or action values of a specific State")

        if not all([t in self._data["StateMachine"]["Transition"].keys() for t in ["in", "out"]]):
            raise SMJSONIntegrityError("in and/or out values of Transition")

        if not all([k in self._data["StateMachine"]["Transition"][t].keys() for k in ["id_in", "id_out", "evaluation"] for t in self._data["StateMachine"]["Transition"].keys()]):
            raise SMJSONIntegrityError("id_in, id_out and/or evaluation of a specific Transition")

    def _generateStateMachineStructure(self):
        """Method that generates StateMachien structure

        Raises:
            FileNotFoundError: raise an error the file leading to the functions definition doesn't exist
        """
        if not os.path.isfile(self._data["path"]):
            file_sm = open(self._data["path"], "w+")
            # os.mknod(self._data['path'])
            # raise FileNotFoundError
        else:
            file_sm = open(self._data["path"], "r+")

        lines = file_sm.readlines()

        for v in self._data["StateMachine"]["Variable"].keys():
            if True not in [v in l for l in lines]:
                file_sm.write(v + " = " + str(self._data["StateMachine"]["Variable"][v]) + "\n")

        for s in self._data["StateMachine"]["State"].keys():
            if True not in ["def " + self._data["StateMachine"]["State"][s]["action"] in l for l in lines]:
                file_sm.write("def " + self._data["StateMachine"]["State"][s]["action"] +"():\n\t#TODO\n\tpass\n\n")

            # self.addState(self._data["StateMachine"]["State"][s], self._data["path"])

        for t in self._data["StateMachine"]["Transition"].keys():
            if True not in ["def " + self._data["StateMachine"]["Transition"][t]["evaluation"] in l for l in lines]:
                file_sm.write("def " + self._data["StateMachine"]["Transition"][t]["evaluation"] +"():\n\t#TODO\n\tpass\n\n")

            # self.addTransition(self._data["StateMachine"]["Transition"][t], self._data["path"])

        file_sm.close()

        for s in self._data["StateMachine"]["State"].keys():
            self.addState(self._data["StateMachine"]["State"][s], self._data["path"])

        for t in self._data["StateMachine"]["Transition"].keys():
            self.addTransition(self._data["StateMachine"]["Transition"][t], self._data["path"])

    def loadJSON(self, path:str):
        """Method that loads JSON file
        """
        json_file = open(path)


        self._data = json.load(json_file)
        json_file.close()

        if "SM" not in self._data.keys():
            raise SMJSONIntegrityError("SM key not in JSON file")

        self._data = self._data["SM"]

        self._checkJSONIntegrity()
        self._generateStateMachineStructure()

    def _dumpJSON(self, name:str):
        """Method that saves StateMachine  to a JSON file
        """
        pass

    def __repr__(self):
        """Redefined method to print value of the StateMachine class instance

        Returns:
            str: printable value of StateMachine class instance
        """
        s = "State Machine name: " + self._name + "\n"

        for st in self._states.keys():
            s += self._states[st].__repr__() + "\n"

        for tr in self._transitions.keys():
            s += self._transitions[tr].__repr__() + "\n"

        return s