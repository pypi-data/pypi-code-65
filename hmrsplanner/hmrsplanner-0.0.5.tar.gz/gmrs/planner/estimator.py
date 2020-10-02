from typing import Type
from collections.abc import Iterable
import itertools

from gmrs.evaluation.outcome import Outcome

from gmrs.planner.submodel import SubModel
from gmrs.planner.submodel import ConstantEvaluationSubmodel, RefinedSubmodel
from gmrs.planner.submodel import MultipleConstantEvaluationsSubmodel

from gmrs.objective.objective_system import ObjectiveSystem
from .operators.ievaluator import IEvaluator


class Estimator:
    objective_systems: [ObjectiveSystem] = []
    operators = dict()

    def __init__(self):
        pass

    def eval_op(self, op, submodels: [SubModel]):
        operator: IEvaluator = self.operators[op]
        return operator.eval(submodels)

    def eval_single(self, model):
        if isinstance(model, ConstantEvaluationSubmodel):
            return model.evaluation
        elif isinstance(model,  MultipleConstantEvaluationsSubmodel):
            return model.eval()
        elif isinstance(model, RefinedSubmodel):
            op = model.op
            return self.eval_op(op, model.refinements)
        else:
            mt = model.__class__.__name__
            err = f'trying to evaluate not supported model type {mt}'
            raise Exception(err)

    def combineGen(self, gena, genb, func):
        a = gena if isinstance(gena, Iterable) else [gena]
        b = genb if isinstance(genb, Iterable) else [genb]
        return itertools.starmap(func, itertools.product(a, b))

    def seq_agg(self, res_out: Outcome,
                outcome1: Outcome, outcome2: Outcome):
        ''' aggregate properties of outcomes occurring sequentially '''
        for q in self.objective_systems:
            q.seq_agg(res_out, outcome1, outcome2)

    def merge_configs(self, config1: dict, config2: dict) -> dict:
        nconfig = dict()
        nconfig.update(config1)
        for key, value in config2.items():
            c1_value = nconfig.get(key)
            if c1_value is not None and c1_value != value:
                # TODO handle warn
                print('warn: merging configs with conflicting name space: {key}')
        nconfig.update(config2)
        return nconfig


# Factory

def estimatorFactory(
            operators: [],  # operators: [Type[Operator]],
            objective_systems: [Type[ObjectiveSystem]]) -> Estimator:

    estimator = Estimator()

    for operator in operators:
        op = operator(estimator)
        estimator.operators[op.code] = op

    estimator.objective_systems = objective_systems
    return estimator
