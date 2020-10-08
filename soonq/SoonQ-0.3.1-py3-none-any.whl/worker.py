"""Implements worker classes.

Classes:
Worker
"""

import pickle
import sys
import traceback

from .utils import echo


class Worker:
    """Basic worker class.

    Example Usage:
        task = AdderTask()
        worker = Worker(task=task)
        worker.start()
    """

    def __init__(self, task):
        self.task = task
        self.waiting = False

    def start(self):
        """Begin working on the assigned type of task."""
        while True:
            try:
                # Read database.
                dequeued_item = self.task.dequeue()
                if not dequeued_item:
                    if not self.waiting:
                        echo(f"Waiting for next task... (Ctrl + C to quit)\n")
                        self.waiting = True
                    continue
                self.waiting = False
                self.task.set_status('dequeued')
                task_id, _, _, _, task_args, task_kwargs = dequeued_item
                task_args = pickle.loads(task_args)
                task_kwargs = pickle.loads(task_kwargs)
                # Run.
                exc_info = None
                echo(f"Running task: {task_id}")
                self.task.set_status('running')
                try:
                    self.task.run(*task_args, **task_kwargs)
                except:
                    # Any Exceptions will be saved.
                    exc_info = list(sys.exc_info())
                    exc_info[-1] = traceback.extract_tb(exc_info[-1])
                if exc_info:
                    echo(f"Error in task: {task_id}\n")
                    self.task.set_status('error')
                    self.task.record_exc(*exc_info)
                else:
                    echo(f"Finished task: {task_id}\n")
                    self.task.set_status('complete')
            except KeyboardInterrupt:
                self.quit()
                break

    def quit(self):
        """Stop working."""
        echo("Quitting")
