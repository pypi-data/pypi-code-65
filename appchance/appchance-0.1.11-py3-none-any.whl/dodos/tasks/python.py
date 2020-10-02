from doit.tools import Interactive
from doit.action import CmdAction

def task_build_pkg():
    """ Build python package """
    return {
      "actions": [
          "python setup.py sdist bdist_wheel",
          "twine upload dist/*"
      ]
    }
