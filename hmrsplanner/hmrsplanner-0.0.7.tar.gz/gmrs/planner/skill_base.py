import abc
from enum import Enum

from gmrs.graph.node import Node


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


class SkillBase:
    name = '_'
    status = SkillStatus.unbound

    def __init__(self, *params):
        self.init(*params)

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
