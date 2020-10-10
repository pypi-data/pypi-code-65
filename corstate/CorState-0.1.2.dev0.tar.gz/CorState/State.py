'''
File: State.py
Created Date: Sunday, July 0th 2020, 12:13:46 am
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
2020-09-17	Zen	Adding encapsulated state
2020-09-12	Zen	Updating init by JSON file
2020-09-12	Zen	Updating some comments
2020-09-11	Zen	Updating import module
2020-09-10	Zen	Refactoring the State structure
'''


from .CorStateError import *
import importlib


class State:
    """State class
    """
    _nb_state = 0

    def __init__(self):
        """Class constructor
        """
        self._id = State._nb_state
        State._nb_state = State._nb_state + 1

        self._action = None
        self._encapsulation = False

    def getID(self) -> int:
        """Method that returns State ID

        Returns:
            int: State ID
        """
        return self._id

    def initBySFF(self, sff:dict, module:str):
        """Method that initialzes a State from a JSON file

        Args:
            sff (dict): state from file
            module (str): module information
        """
        module_name = module

        if module_name[len(module_name)-3:] != ".py":
            raise SMExtensionName

        if module_name[:2] != "./":
            raise SMRelativePathFile

        module_name = module_name[2:]
        module_name = module_name[:len(module_name)-3]
        module_name = module_name.replace('/', '.')


        self.mod = importlib.import_module(module_name, module)
        globals().update(self.mod.__dict__)

        self._id = sff["id"]
        self._action = getattr(self.mod, sff["action"])
        self._encapsulation = sff['encapsulation']

    def addAction(self, action):
        """Method that adds action to this state

        Args:
            action ([type]): action that will be executed by this state
        """
        self._action = action

    def run(self):
        """Method that will run the action defined to this state
        """
        self._action()

    def setEncapsulation(self, value:bool):
        self._encapsulation = value

    def getEncapsulation(self) -> bool:
        return self._encapsulation

    def __repr__(self) -> str:
        """Redefined method to print value of the State class instance

        Returns:
            str: printable value of State class instance
        """
        s = "State id: " + str(self._id)

        return s