from gmrs.planner.outcome import Outcome

from enum import Enum


class PropertyType(Enum):
    COST = 1
    REWARD = 2


class Property:
    @staticmethod
    def seq_agg(res: Outcome, outcome1: Outcome, outcome2: Outcome):
        pass

    @staticmethod
    def to_cost(outcome: Outcome):
        pass
