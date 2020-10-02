from gmrs.evaluation.outcome import Outcome, is_success
from .objective_system import ObjectiveSystem


class Probability(ObjectiveSystem):

    @staticmethod
    def seq_agg(res_outcome: Outcome, outcome1: Outcome, outcome2: Outcome):
        res_outcome.p = outcome1.p * outcome2.p

    @staticmethod
    def success_rate(outcomes: [Outcome]):
        res = 0.0
        for out in outcomes:
            if is_success(out):
                res += out.p
        return res
