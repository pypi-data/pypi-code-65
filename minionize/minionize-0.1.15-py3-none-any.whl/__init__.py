from abc import ABC, abstractmethod
import logging
import os
from pathlib import Path
import time
import traceback
from typing import Callable

from dotenv import load_dotenv

from .env import (
    ENGINE,
    ENGINE_EXECO,
    ENGINE_GOOGLE,
    ENV_DRY_MODE,
    ENGINE_PULSAR,
)
from .reporter import Reporter, Event, create_reporter
from .types import Param

# first thing first ... load dotenv file if any in the cwd
load_dotenv(dotenv_path=Path.cwd() / ".env")

LOGGER = logging.getLogger(__name__)

# event names
EVENT_PRE_SETUP = "pre-setup"
EVENT_POST_SETUP = "post-setup"
EVENT_PRE_PROCESS = "pre-process"
EVENT_POST_PROCESS = "post-process"
EVENT_PRE_TEARDOWN = "pre-teardown"
EVENT_POST_TEARDOWN = "post-teardown"


class Engine(ABC):
    """Base class for our Engines.

    An engine is responsible for getting data(param) from a queue.
    It acknowleges (positively or negatively) the data back to the queue.
    The exact semantic of ack/nack is still under intense discussion. Please
    refer to the concrete implementation for further information.
    """

    @abstractmethod
    def next(self) -> Param:
        pass

    @abstractmethod
    def ack(self, param: Param):
        pass

    @abstractmethod
    def nack(self, param: Param):
        pass


class Callback(ABC):
    """Base class for the (user defined) callbacks.

    A Callback modelizes the behaviour of the application inputs/outputs.
    """

    @abstractmethod
    def setup(self, param: Param, engine: Engine):
        """Called right after a new param is fetched from the queue."""
        pass

    @abstractmethod
    def process(self, param: Param, engine: Engine):
        """This is where process will happen."""
        pass

    @abstractmethod
    def teardown(self, param: Param, engine: Engine, exception: Exception):
        """Called at the before a new iteration."""
        pass

    def dry_mode(self):
        return os.getenv(ENV_DRY_MODE) is not None


class PrintCallback(Callback):
    """Dummy callback for debug purpose.

    Acknowledges right after printing. It never uses nack.
    """

    def setup(self, param, engine):
        print(f"setup {param}")

    def process(self, param, engine):
        print(f"process {param}")
        engine.done(param)

    def teardown(self, param, engine, exception):
        print(f"finished {param}")


class DefaultCallback(Callback):
    """A good enough callback.

    It's designed to be a good enough callback for most use cases. User must
    subclass it and define at least the process method.
    incoming param.
    - Acknowlege if the sub process return code is 0
    - Nack otherwise
    """

    def setup(self, param, engine):
        return super().setup(param, engine)

    def teardown(self, param, engine, exception):
        if exception is None:
            # everything is alright
            self.teardown_ok(param, engine)
            # we ack when ok hook has been successfully ran
            engine.ack(param)
            return
        try:
            raise exception
        except KeyboardInterrupt:
            engine.nack(param)
            raise exception
        except Exception:
            pass
        finally:
            engine.nack(param)
            self.teardown_ko(param, engine, exception)

    def teardown_ok(self, param, engine):
        pass

    def teardown_ko(self, param, engine, exception):
        pass


class ProcessCallback(DefaultCallback):
    """A callback that spawn a process upon the reception of params.

    User must at least define the to_cmd method that tells how the params are
    passed to the subprocess.
    """

    def to_cmd(self, param: Param):
        return f"echo {param}"

    def process(self, param: Param, engine: Engine):
        import subprocess

        if self.dry_mode():
            print(f"[dry mode] {self.to_cmd(param)}")
        else:
            try:
                subprocess.run(self.to_cmd(param), shell=True, check=True)
            except Exception as e:
                raise e


class FuncCallback(DefaultCallback):
    """A callback that minionizes a python function.

    User must pass the function to minionize in parameter
    """

    def __init__(self, func: Callable[[Param], None]):
        self.func = func

    def process(self, param: Param, engine: Engine):
        return self.func(param)


class EntryPoint:
    """This is the framework.

    It's mainly a loop that continuously fetch the next param and call the
    callback methods.
    """

    def __init__(self, callback: Callback, engine: Engine, reporter: Reporter):
        self.cb = callback
        self.engine = engine
        self.reporter = reporter

    def run(self):
        """Routine."""
        generation = 0
        while True:
            # prepare next iteration
            generation += 1
            event = Event(generation)

            # get next param in the queue
            LOGGER.debug("get next param")
            param = event.timeit(self.engine.next)()
            event.param = param

            exception = None
            if param is None:
                LOGGER.debug("No more params to handle, leaving")
                break
            try:
                # The user may want the setup to fail
                # so we let the teardown decides what
                # to do in this case
                LOGGER.debug(param)

                # setup
                event.timeit(self.cb.setup)(param, self.engine)

                # process
                event.timeit(self.cb.process)(param, self.engine)
            except Exception as e:
                exception = e
                event.error = e
                LOGGER.error(
                    "--> exception raised during execution" "(printing stack trace)"
                )
                LOGGER.error(traceback.format_exc())

            # teardown
            event.timeit(self.cb.teardown)(param, self.engine, exception)

            try:
                # we don't want the following to hinder the experiment
                # so we catch any error here
                event.end = time.time()
                self.reporter.fire(event)
            except Exception:
                LOGGER.error("Reporter fails to send its status")


def create_engine():
    if ENGINE == ENGINE_EXECO:
        from minionize.execo import Execo

        return Execo.from_env()

    if ENGINE == ENGINE_GOOGLE:
        from minionize.google import GooglePubSub

        return GooglePubSub.from_env()

    if ENGINE == ENGINE_PULSAR:
        from minionize.pulsar import PulsarPubSub

        return PulsarPubSub.from_env()

    raise Exception(f"EntryPoint {ENGINE} not supported")


def minionizer(callback: Callback):
    """Take a user callback and minionize it !"""
    # NOTE(msimonin): use dotenv
    engine = create_engine()
    reporter = create_reporter()

    return EntryPoint(callback, engine, reporter)
