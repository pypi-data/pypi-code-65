from abc import ABC, abstractclassmethod, abstractmethod
from functools import wraps
import logging
import os
import pandas as pd
from pathlib import Path
from typing import Mapping, List, Optional
from uuid import uuid4
import time

from ..env import (
    REPORTER,
    REPORTER_STDOUT,
    REPORTER_JSON,
    ENV_REPORTER_JSON_DIRECTORY,
    DEFAULT_JSON_REPORTER_DIRECTORY,
)
from ..types import Param

LOGGER = logging.getLogger(__name__)

ENV_VARS = ["OAR_JOB_ID"]


class Event:
    def __init__(self, generation: int):
        self.generation = generation
        self._start = time.time()
        self._atomic_actions: List = []
        self._end: Optional[float] = None
        self._param: Optional[Param] = None
        self._error: Optional[Exception] = None
        # capture some of the env here OAR_JOB_ID if any, hostname ...
        self._extra: Mapping = {}
        self._fill_with_env()

    def __repr__(self):
        return (
            f"<Event ({id(self)}) "
            f"generation={self.generation} "
            f"start={self._start} "
            f"end={self.end } "
            f"error={str(self.error)} "
            f"param={self.param} "
            f"atomic_actions={self._atomic_actions} >"
        )

    def _fill_with_env(self):
        for env_var in ENV_VARS:
            if os.getenv(env_var) is not None:
                self._extra.update(oar_job_id=os.getenv(env_var))
        self._extra.update(nodename=os.uname().nodename)

    @property
    def param(self) -> Param:
        return self._param

    @param.setter
    def param(self, param: Param):
        self._param = param

    @property
    def error(self) -> Optional[Exception]:
        return self._error

    @error.setter
    def error(self, error: Optional[Exception]):
        self._error = error

    @property
    def end(self) -> Optional[float]:
        return self._end

    @end.setter
    def end(self, end: float):
        self._end = end

    def to_dict(self) -> Mapping:
        e = None
        if self._error is not None:
            e = str(self._error)
        d = dict(
            genation=self.generation,
            start=self._start,
            end=self._end,
            param=self._param,
            error=e,
            atomic_actions=self._atomic_actions,
            **self._extra,
        )
        return d

    def timeit(self, f):
        """A decorator that add custom atomic action to the event.

        The rationale is to pass that to the user code, so that the user can
        register custom action.
        """

        @wraps(f)
        def wrapped(*args, **kwargs):
            start = time.time()
            r = None
            exception = None
            try:
                r = f(*args, **kwargs)
            except Exception as e:
                exception = e
            finally:
                end = time.time()
                name = getattr(f, "__name__", "unknown")
                atomic_action = dict(name=name, start=start, end=end)
                self._atomic_actions.append(atomic_action)
                if exception is None:
                    return r
                else:
                    raise exception

        return wrapped


class Reporter(ABC):
    """Base class for our reporters."""

    def __init__(self, **kwargs):
        self.extra = kwargs

    @abstractmethod
    def fire(self, event: Event):
        """Fire an event to the reporter.

        Args:
            name: name of the event
            value: content of the event
        """
        pass

    @abstractmethod
    def to_pandas(self) -> pd.DataFrame:
        return pd.DataFrame()

    @abstractclassmethod
    def from_env(cls):
        pass


class StdoutReporter(Reporter):
    def fire(self, event: Event):
        print(event)

    def to_pandas(self) -> pd.DataFrame:
        return pd.DataFrame()

    @classmethod
    def from_env(cls):
        return cls()


class NullReporter(Reporter):
    def fire(self, event: Event):
        pass

    def to_pandas(self) -> pd.DataFrame:
        return pd.DataFrame()

    @classmethod
    def from_env(cls):
        return cls()


class JsonReporter(Reporter):
    """Report events in a jsonp file."""

    def __init__(self, directory: Path, **kwargs):
        super().__init__(**kwargs)
        self.directory = directory
        self._uid = uuid4()
        self.target_file = directory / str(self._uid)
        self._buffer: List = []
        self.directory.mkdir(parents=True, exist_ok=True)

    def fire(self, event: Event):
        # force new ref
        self._buffer.append(event)
        self._flush()

    def _flush(self):
        import json

        with self.target_file.open("a+") as f:
            for event in self._buffer:
                json.dump(event.to_dict(), f)
                f.write("\n")
        self._buffer = []

    def to_pandas(self) -> pd.DataFrame:
        df = pd.DataFrame()
        for p in self.directory.glob("*"):
            LOGGER.debug(f"Reading {p}")
            df = pd.concat([df, pd.read_json(p, lines=True)])
        return df

    @classmethod
    def from_env(cls):
        import os

        directory = Path(
            os.getenv(ENV_REPORTER_JSON_DIRECTORY, DEFAULT_JSON_REPORTER_DIRECTORY)
        )
        return cls(directory)


def create_reporter() -> Reporter:
    if REPORTER == REPORTER_STDOUT:
        return StdoutReporter.from_env()

    if REPORTER == REPORTER_JSON:
        return JsonReporter.from_env()

    return NullReporter.from_env()
