import collections
import numbers

import six

from savvihub.savvihub_cli.config import config as global_config
from savvihub import history


class Experiment:
    def __init__(self, experiment_id):
        self.experiment_id = experiment_id
        self._history = None

    @classmethod
    def from_given_or_global_config(cls, config):
        if not config:
            config = global_config
        experiment = cls(config.experiment_id)
        return experiment

    @property
    def history(self):
        if not self._history:
            self._history = history.History(self)
        return self._history

    def log(self, step, row=None):
        if not row:
            row = dict()

        if not isinstance(row, collections.Mapping):
            raise ValueError(".log() takes a dictionary as a parameter")

        if any(not isinstance(key, six.string_types) for key in row.keys()):
            raise ValueError("The key of dictionary in .log() parameter must be str")

        for k in row.keys():
            if not k:
                raise ValueError("Logging empty key is not supported")

        if not isinstance(step, numbers.Number):
            raise ValueError(f"Step must be a number, not {type(step)}")
        if step < 0:
            raise ValueError(f"Step must be a positive integer, not {step}")
        if not isinstance(type(step), int):
            step = int(round(step))

        self.history.update(step, row)
