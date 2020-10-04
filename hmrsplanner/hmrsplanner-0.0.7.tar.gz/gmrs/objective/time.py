from gmrs.planner.outcome import Outcome
from .property_base import Property


class Time(Property):

    code = 't'

    @staticmethod
    def seq_agg(res_outcome: Outcome, outcome1: Outcome, outcome2: Outcome):
        code = Time.code
        res_outcome[code] = outcome1[code] + outcome2[code]

    @staticmethod
    def to_cost(outcome):
        return outcome.get(Time.code)
