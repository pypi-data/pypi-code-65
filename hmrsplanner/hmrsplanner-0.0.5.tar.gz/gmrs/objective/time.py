from gmrs.evaluation.outcome import Outcome
from .objective_system import ObjectiveSystem


class Time(ObjectiveSystem):

    id = 't'

    @staticmethod
    def seq_agg(res_outcome: Outcome, outcome1: Outcome, outcome2: Outcome):
        res_outcome[id] = outcome1[id] + outcome2[id]
