from doit.tools import Interactive
from doit.action import CmdAction
from dodos.config import DOCKER_COMPOSE_CMD, DJANGO_SERVICE_NAME, DJANGO_APPS_DIR


def task_build_pkg():
    """ Build python package """
    return {
      "actions": [
          "python setup.py sdist bdist_wheel",
          "twine upload dist/*"
      ]
    }
