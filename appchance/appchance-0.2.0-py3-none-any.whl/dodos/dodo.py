import importlib
from doit.tools import Interactive

from appchance.dodos.config import TASK_MODULES, CUSTOM_TASKS

DOIT_CONFIG = {
    'backend': 'sqlite3',
    'dep_file': '.ddb.sql3',
}


def load_tasks(module_names, prepend=''):

    for task_module in module_names:
        tasks = importlib.import_module(f'appchance.dodos.tasks.{prepend}{task_module}')

        names = [x for x in tasks.__dict__ if not x.startswith("_")] # skip underscore functions
        globals().update({k: getattr(tasks, k) for k in names})


load_tasks(TASK_MODULES)
load_tasks(CUSTOM_TASKS, prepend='custom.')
