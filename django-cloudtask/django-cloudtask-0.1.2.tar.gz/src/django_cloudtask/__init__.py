from .task import Task, register_task

__version__ = "0.1.2"

__all__ = ["register_task", "Task"]

default_app_config = "django_cloudtask.apps.TasksConfig"
