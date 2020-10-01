from .base import TaskStrategy
from .call_function import FunctionTask, ParamsNotDefined
from .generate_file import GenerateFileTask
from .load_variables import LoadVariablesTask
from .set_variables import SetVariablesTask

STANDARD_TASKS = (
    LoadVariablesTask,
    SetVariablesTask,
    FunctionTask,
    GenerateFileTask,
)
