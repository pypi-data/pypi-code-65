'''
File: CoStateError.py
Created Date: Sunday, July 0th 2020, 12:36:03 am
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
2020-09-12	Zen	Adding new exception
'''


class SMAddingStateError(Exception):
    """Class focused on catching objects that can be casted into a State

    Args:
        Exception (Exception): Exception
    """
    def __init__(self, message="This value can me casted into a State."):
        """Class constructor

        Args:
            message (str, optional): message. Defaults to "This value can me casted into a State.".
        """
        self.message = message
        super().__init__(self.message)

class SMAddingTransitionError(Exception):
    """Class focused on catching objects that can be casted into a Transition

    Args:
        Exception (Exception): Exception
    """
    def __init__(self, message="This value can me casted into a Transition."):
        """Class constructor

        Args:
            message (str, optional): message. Defaults to "This value can me casted into a Transition.".
        """
        self.message = message
        super().__init__(self.message)

class SMIntegrityError(Exception):
    """Class focused on catching missing initial or final transition

    Args:
        Exception (Exception): Exception
    """
    def __init__(self, more:str, message=" transition missing or not assigned to a State."):
        """Class constructor

        Args:
            more (str): specify the missing transition
            message (str, optional): message. Defaults to " transition missing or ont assigned to a State.".
        """
        self.message = more + message
        super().__init__(self.message)

class SMJSONIntegrityError(Exception):
    """Class focused on catching missing initial or final transition

    Args:
        Exception (Exception): Exception
    """
    def __init__(self, more:str, message=" are missing into the JSON file."):
        """Class constructor

        Args:
            more (str): specify missing elements
            message (str, optional): message. Defaults to " are missing into the JSON file.".
        """
        self.message = more + message
        super().__init__(self.message)

class SMExtensionName(Exception):
    """Class focused on catching wrong extension file

    Args:
        Exception (Exception): Exception
    """
    def __init__(self, message="File must be python file."):
        """Class constructor

        Args:
            message (str, optional): message. Defaults to "File must be python file.".
        """
        self.message = message
        super().__init__(self.message)

class SMRelativePathFile(Exception):
    """Class focused on catching when file path is not realtive

    Args:
        Exception (Exception): Exception
    """
    def __init__(self, message="Python path file must be relative."):
        """Class constructor

        Args:
            message (str, optional): message. Defaults to "Python path file must be relative.".
        """
        self.message = message
        super().__init__(self.message)