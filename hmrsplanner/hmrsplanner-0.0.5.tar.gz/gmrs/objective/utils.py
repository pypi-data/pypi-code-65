from gmrs.evaluation.outcome import Outcome
from gmrs.objective.objective_system import ObjectiveSystem


def seq_agg_all(res_out: Outcome,
                outcome1: Outcome, outcome2: Outcome,
                quality_operators: [ObjectiveSystem]):
    ''' aggregate properties of outcomes occurring sequentially '''
    for q in quality_operators:
        q.seq_agg(res_out, outcome1, outcome2)

