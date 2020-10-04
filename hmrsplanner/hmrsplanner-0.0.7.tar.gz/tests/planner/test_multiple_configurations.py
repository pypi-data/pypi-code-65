import pytest

from gmrs.util.model import constant_outcomes

from gmrs.planner.evaluation import Evaluation
from gmrs.planner.operators.sequential import Sequential, SEQ_OP
from gmrs.planner.submodel import MultipleConstantEvaluationsSubmodel
from gmrs.planner.submodel import ConstantEvaluationSubmodel

from gmrs.objective.probability import Probability

from gmrs.planner.estimator import Estimator, estimatorFactory

from .utils import evaluationIn

estimator: Estimator = estimatorFactory(
    operators=[Sequential],
    objective_systems=[Probability])

moveSlow = Evaluation({'speed': 'slow'}, constant_outcomes(0.9, time=3))
moveFast = Evaluation({'speed': 'fast'}, constant_outcomes(0.8, time=2))
actionX = Evaluation({'config_action': 'x'}, constant_outcomes(0.7, time=8))
actionY = Evaluation({'config_action': 'y'}, constant_outcomes(0.6, time=9))

twin_then_single_submodels = [
    MultipleConstantEvaluationsSubmodel(moveSlow, moveFast),
    ConstantEvaluationSubmodel(actionX)
]

twin_then_twin_submodels = [
    MultipleConstantEvaluationsSubmodel(moveSlow, moveFast),
    MultipleConstantEvaluationsSubmodel(actionX, actionY),
]


def test_seq_twin_with_single():
    evaluations = estimator.eval_op(SEQ_OP, twin_then_single_submodels)
    for evaluation in evaluations:
        sr = Probability.success_rate(evaluation.outcomes)
        evaluationIn(evaluation.config, sr,
                     ({'speed': 'slow', 'config_action': 'x'}, 0.63),
                     ({'speed': 'fast', 'config_action': 'x'}, 0.56))
        print(sr)


def test_twin_with_twin():
    evaluations = estimator.eval_op(SEQ_OP, twin_then_twin_submodels)
    for evaluation in evaluations:
        sr = Probability.success_rate(evaluation.outcomes)
        evaluationIn(evaluation.config, sr,
                     ({'speed': 'slow', 'config_action': 'x'}, 0.63),
                     ({'speed': 'fast', 'config_action': 'x'}, 0.56),
                     ({'speed': 'slow', 'config_action': 'y'}, 0.54),
                     ({'speed': 'fast', 'config_action': 'y'}, 0.48))
        print(sr)
