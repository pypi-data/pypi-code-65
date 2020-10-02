from doit.tools import Interactive
from doit.action import CmdAction

def task_build_pkg():
    """ Build python package """
    return {
      "actions": [
          Interactive("echo dupa"),
      ]
    }
