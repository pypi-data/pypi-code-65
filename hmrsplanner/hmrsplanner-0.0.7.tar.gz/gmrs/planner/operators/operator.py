
import abc

from gmrs.planner.evaluation import Evaluation

from ..submodel import IEvaluable
from ..estimator import Estimator


class Operator:
    base: Estimator = None

    def __init__(self, base):
        self.base = base

    @abc.abstractclassmethod
    def eval(self, submodel: IEvaluable) -> [Evaluation]:
        pass

