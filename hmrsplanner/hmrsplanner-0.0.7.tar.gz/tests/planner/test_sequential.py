
import pytest

from gmrs.planner.submodel import ConstantEvaluationSubmodel, RefinedSubmodel
from gmrs.util.model import constant_outcomes

from gmrs.planner.operators.sequential import Sequential, SEQ_OP
from gmrs.planner.evaluation import Evaluation

from gmrs.objective.probability import Probability

from gmrs.planner.estimator import Estimator, estimatorFactory


# container = containers.Container()
# container.configure_logging()
# container.config.from_ini('config.ini')


evaluationA = Evaluation({'config1': 'a'}, constant_outcomes(0.9))
evaluationB = Evaluation({'config2': 'b'}, constant_outcomes(0.8))
evaluationC = Evaluation({'config3': 'c'}, constant_outcomes(0.7))

two_submodels = [
    ConstantEvaluationSubmodel(evaluationA),
    ConstantEvaluationSubmodel(evaluationB)
    ]

three_submodels = [
    ConstantEvaluationSubmodel(evaluationA),
    ConstantEvaluationSubmodel(evaluationB),
    ConstantEvaluationSubmodel(evaluationC)
    ]

submodels_with_mixed_refinement = [
    ConstantEvaluationSubmodel(evaluationA),
    ConstantEvaluationSubmodel(evaluationB),
    RefinedSubmodel(SEQ_OP,
                    [ConstantEvaluationSubmodel(evaluationA),
                     ConstantEvaluationSubmodel(evaluationB)])
]


estimator: Estimator = estimatorFactory(
    operators=[Sequential],
    objective_systems=[Probability])


def test_eval_seq_two_submodels():
    evaluation = next(estimator.eval_op(SEQ_OP, two_submodels))
    sr = Probability.success_rate(evaluation.outcomes)
    assert 0.72 == pytest.approx(sr)
    print(sr)


def test_eval_seq_three_submodels():
    evaluation = next(estimator.eval_op(SEQ_OP, three_submodels))
    sr = Probability.success_rate(evaluation.outcomes)
    assert 0.504 == pytest.approx(sr)
    print(sr)


def test_eval_seq_with_mixed_refinement():
    evaluation = next(estimator.eval_op(SEQ_OP,
                      submodels_with_mixed_refinement))
    sr = Probability.success_rate(evaluation.outcomes)
    assert 0.5184 == pytest.approx(sr)
    print(sr)


# from gmrs.planner.quality.time import Time
