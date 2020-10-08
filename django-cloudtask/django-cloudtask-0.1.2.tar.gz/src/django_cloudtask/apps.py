import os
from importlib import import_module

from django.apps import AppConfig


class TasksConfig(AppConfig):
    name = "tasks"

    def ready(self):
        # go through all apps and register tasks.
        dirname = os.path.dirname(self.path)
        for cfg in self.apps.get_app_configs():
            path = cfg.path
            if os.path.dirname(path) != dirname:
                continue

            module = os.path.relpath(cfg.path, dirname).replace("/", ".")
            try:
                import_module(f"{module}.tasks")
            except ImportError as e:
                if f"{module}.tasks" not in str(e):
                    raise
                continue
