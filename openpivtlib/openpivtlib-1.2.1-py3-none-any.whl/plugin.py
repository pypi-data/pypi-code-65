import logging
from typing import Optional
from . import util


class Plugin:
    def __init__(self, workflow: str, job_id: int, args: Optional[dict] = None):
        self.workflow = workflow
        self.job_id = job_id
        self.args = args if args is not None else {}

        self.logger = PluginLoggerAdapter(util.get_class_logger(self), self.workflow, self.job_id)

    def execute(self, data: Optional[dict] = None) -> Optional[dict]:
        raise NotImplementedError


class Trigger:
    def __init__(self, workflow: str, args: Optional[dict] = None):
        self.workflow = workflow
        self.args = args if args is not None else {}

        self.logger = TriggerLoggerAdapter(util.get_class_logger(self), self.workflow)

    def run(self):
        raise NotImplementedError


class PluginLoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger: logging.Logger, workflow: str, job_id: int):
        super().__init__(logger, {})
        self.workflow = workflow
        self.job_id = job_id

    def process(self, msg, kwargs):
        return f'[{self.workflow}:{self.job_id}] {msg}', kwargs


class TriggerLoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger: logging.Logger, workflow: str):
        super().__init__(logger, {})
        self.workflow = workflow

    def process(self, msg, kwargs):
        return f'[{self.workflow}] {msg}', kwargs
