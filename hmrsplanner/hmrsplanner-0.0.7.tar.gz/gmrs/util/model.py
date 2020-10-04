
from gmrs.planner.outcome import Outcome, Result


def constant_outcomes(p, **rewards):
    return [Outcome(p=p, res=Result.SUCCESS, **rewards),
            Outcome(p=1-p, res=Result.FAILURE)]

