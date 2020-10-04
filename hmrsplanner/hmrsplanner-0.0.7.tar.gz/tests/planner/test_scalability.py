import pytest
import time



from gmrs.util.model import constant_outcomes

from gmrs.planner.operators.sequential import Sequential, SEQ_OP
from gmrs.planner.submodel import MultipleConstantEvaluationsSubmodel
from gmrs.planner.submodel import ConstantEvaluationSubmodel

from gmrs.planner.evaluation import Evaluation

from gmrs.objective.probability import Probability

from gmrs.planner.estimator import Estimator, estimatorFactory
from .utils import evaluationIn


estimator: Estimator = estimatorFactory(
    operators=[Sequential],
    objective_systems=[Probability])


def gen_mult_constant_eval_sub_model(num_tasks, num_confs_per_task):
    submodels = []
    for task in range(0, num_tasks):
        evals = []
        for conf in range(0, num_confs_per_task):
            eval_ = Evaluation({f'conf_t{task}': conf},
                               constant_outcomes(0.99))
            evals.append(eval_)
        m = MultipleConstantEvaluationsSubmodel(*evals)
        submodels.append(m)
    return submodels


def test_tasks_with_multi_confs_submodels():
    num_tasks = 10
    num_confs_per_task  = 4
    space = num_confs_per_task ** num_tasks
    print(f'space of {space}')
    seq_five_of_ten_confs_submodels = gen_mult_constant_eval_sub_model(
        num_tasks=num_tasks, num_confs_per_task=num_confs_per_task)

    start = time.time()
    evaluations = estimator.eval_op(SEQ_OP, seq_five_of_ten_confs_submodels)
    setup = time.time()
    num_evaluations = 0
    times = [None for _ in range(0, 10)]
    for evaluation in evaluations:
        sr = Probability.success_rate(evaluation.outcomes)
        # if num_evaluations > 1000:
        #     break
        
        if num_evaluations < 10:
            times[num_evaluations] = time.time()
        num_evaluations += 1
        # print(evaluation.config)
        # print(sr)
    end = time.time()
    print(f'{(setup - start):.6f} setup')
    print(f'{(times[0] - start):.6f} first evaluation d{times[0]-setup}')
    print(f'{(end - start):.6f} end time')

    last = setup
    for t in times:
        ns = (t - last)*1000*1000
        print(f'others {ns:.2f} ns')
        last = t

    assert num_evaluations == space
