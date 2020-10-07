"""
Module containing types that can be used as input / output for La Mancha blueprints
"""

from typing import NewType

StudentLogin = NewType('StudentLogin', str)
StudentLogin.__doc__ = """\
Type representing a student through their login
"""

ModuleID = NewType('ModuleID', int)
ModuleID.__doc__ = """\
Type representing a module through its ID
"""

ActivityID = NewType('ActivityID', int)
ActivityID.__doc__ = """\
Type representing an activity through its ID
"""

GroupID = NewType('GroupID', int)
GroupID.__doc__ = """\
Type representing a group through its ID
"""

GroupLeader = NewType('GroupLeader', str)
GroupLeader.__doc__ = """\
Type representing a group through their leader login
"""

Stage = NewType('Stage', str)
Stage.__doc__ = """\
Type representing a quest stage through its name
"""
