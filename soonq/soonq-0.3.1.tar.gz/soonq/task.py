"""Implements task classes.

Classes:
BaseTask - Base task class.
"""

import abc
import pickle
import uuid

from .broker import Broker
from .utils import echo


class BaseTask(abc.ABC):
    """Base task class.

    Example Usage:
        class AdderTask(BaseTask):
            task_name = 'AdderTask'
            def run(self, a, b):
                result = a + b
                return result

        adder = AdderTask()
        adder.delay(9, 34)
    """

    # Status options are:
    #   detached - Instantiated, not queued.
    #   enqueued - Queued via Broker.
    #   dequeued - Dequeued via Worker.
    #   running - Running via Worker.
    #   error - Exception encountered during run.
    #   complete - Run complete.
    _status_options = (
        'detached', 'enqueued', 'dequeued', 'running', 'error',
        'complete')

    def __init__(self):
        self.broker = Broker()
        self.set_status('detached')

    @property
    @classmethod
    @abc.abstractmethod
    def task_name(cls):
        pass

    @abc.abstractmethod
    def run(self, *args, **kwargs):
        """Subclasses must implement their business logic here."""
        pass

    def delay(self, *args, **kwargs):
        """Have the broker enqueue this task, thereby delaying its
        execution until some future time.
        """
        try:
            self.task_id = str(uuid.uuid4())
            task = dict(
                task_id=self.task_id,
                args=args,
                kwargs=kwargs,
            )
            self.broker.enqueue(
                item=task, queue_name=self.task_name)
            self.set_status('enqueued')
            echo(f"Queued task: {self.task_id}")
        except Exception:
            raise RuntimeError(
                f"Unable to publish task {self.task_id} to the broker.")

    def dequeue(self):
        """Dequeue one task of this type."""
        item = self.broker.dequeue(queue_name=self.task_name)
        try:
            self.task_id = item['task_id']
        except TypeError:
            self.task_id = None
        return item

    def set_status(self, status):
        """Set status of the BaseTask instance."""
        if status not in self._status_options:
            raise ValueError(f"Task status {status!r} not recognized.")
        self.status = status
        if status == 'running':
            self.broker.add_work(self, status)
        elif status == 'complete':
            self.broker.update_status(self, status)
            self.broker.remove_work(self)

    def record_exc(self, type_, value, traceback):
        """Record the given traceback information."""
        self.broker.update_exc_info(self, type_, value, traceback)

    def __repr__(self):
        return (f"<{self.__class__.__name__}(status={self.status})>")
