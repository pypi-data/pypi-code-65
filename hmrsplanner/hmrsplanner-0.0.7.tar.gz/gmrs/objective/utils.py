from ..planner.outcome import Outcome

from .probability import Probability
from .property_base import Property


def seq_agg_all(res_out: Outcome,
                outcome1: Outcome, outcome2: Outcome,
                quality_operators: [Property]):
    ''' aggregate properties of outcomes occurring sequentially '''
    for q in quality_operators:
        q.seq_agg(res_out, outcome1, outcome2)


def avg_properties(evaluation, objective_systems):
    resp_out = Outcome()
    for os in objective_systems:
        code = os.code
        if issubclass(os, Probability):
            sr = Probability.success_rate(evaluation.outcomes)
            resp_out.set(code, sr)
        else:
            setattr(resp_out, code, 0)
            for outcome in evaluation.outcomes:
                prev = resp_out.get(code)
                weigh = Probability.get(outcome)
                nval = weigh*outcome.get(code) + prev
                setattr(resp_out, code, nval)

    return resp_out
