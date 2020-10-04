import numpy as np
from numpy.testing import assert_array_equal

from gmrs.planner.pareto_front_reducer import is_pareto_efficient
from gmrs.planner.pareto_front_reducer import ParetoFrontReducer
from gmrs.planner.evaluation import Evaluation
from gmrs.planner.submodel import MultipleConstantEvaluationsSubmodel
from gmrs.planner.submodel import RefinedSubmodel
from gmrs.util.model import constant_outcomes
from gmrs.objective.objective import Objective
from gmrs.objective import time, probability

from gmrs.planner.estimator import estimatorFactory, Estimator

from gmrs.planner.operators.sequential import SEQ_OP, Sequential


def test_is_pareto_efficient():
    costs = np.array([[1, 2], [3, 4], [2, 1], [1, 1]])
    res = is_pareto_efficient(costs)
    assert_array_equal([False, False, False,  True], res)


moveFast = Evaluation({'speed': 'fast'}, constant_outcomes(0.9, time=2))
moveSlow = Evaluation({'speed': 'slow'}, constant_outcomes(0.92, time=3))

actionX = Evaluation({'config_action': 'x'}, constant_outcomes(0.8, time=8))
actionY = Evaluation({'config_action': 'y'}, constant_outcomes(0.7, time=9))


twin_then_twin_submodels = [
    MultipleConstantEvaluationsSubmodel(moveSlow, moveFast),
    MultipleConstantEvaluationsSubmodel(actionX, actionY),
]

set_ref = RefinedSubmodel(SEQ_OP,
                          twin_then_twin_submodels)


estimator: Estimator = estimatorFactory(
    operators=[Sequential],
    objective_systems=[probability.Probability],
    reducer=ParetoFrontReducer)


def test_costs_reduce_to_pareto_front():
    eval_ = estimator.eval_single(set_ref)
    print(eval_)
# costs = [
#     {'time': 5, 'energy': 31, 'p': 0.82},
#     {'time': 3, 'energy': 30, 'p': 0.8},
#     {'time': 2, 'energy': 32, 'p': 0.8},
# ]
