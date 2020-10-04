from gmrs.planner.outcome import Outcome, is_success
from .property_base import Property


class Probability(Property):
    code = 'p'

    @staticmethod
    def seq_agg(res_outcome: Outcome, outcome1: Outcome, outcome2: Outcome):
        v1 = outcome1.get(Probability.code)
        v2 = outcome2.get(Probability.code)
        res_outcome.set(Probability.code, v1 * v2)

    @staticmethod
    def get(outcome):
        return outcome.get(Probability.code)

    @staticmethod
    def to_cost(outcome):
        return -1 * outcome.get(Probability.code)

    @staticmethod
    def success_rate(outcomes: [Outcome]):
        res = 0.0
        for out in outcomes:
            if is_success(out):
                res += out.p
        return res
