import abc
import itertools

from enum import Enum
from typing import Iterable, TypeVar, Generic

from gmrs.graph.node import Node
from ..planner.submodel import IEvaluable


class SkillStatus(Enum):
    unbound = 0
    check_and_bind = 1
    expand = 2
    wait = 3
    cancel = 4
    deploy = 5
    execute = 6
    report = 7
    end = 8


T = TypeVar('T')


class ConfigValue(Generic[T]):
    def __init__(self, code: str, value: T):
        self.code = code
        self.value = value


class SkillPlannerBase(IEvaluable):
    name = '_'
    status = SkillStatus.unbound

    def __init__(self, *params):
        self.init(*params)
        self.configs = []

    def add_config(self, config_type_key: str,
                   iterable: Iterable[ConfigValue]):
        self.configs.append((config_type_key, iterable))

    def eval(self):
        config = self.config_iterator()
        return itertools.starmap(config, self.eval_config)

    @abc.abstractmethod
    def eval_config(self, **params):
        pass

    @abc.abstractmethod
    def check_and_bind(self):
        pass

    @abc.abstractmethod
    def expand(self):
        pass

    @abc.abstractmethod
    def wait(self):
        pass

    @abc.abstractmethod
    def cancel(self):
        pass

    @abc.abstractmethod
    def deploy(self):
        pass

    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    def report(self):
        pass

    @abc.abstractmethod
    def end(self):
        pass

    def to_node(self):
        return Node(self.name)
