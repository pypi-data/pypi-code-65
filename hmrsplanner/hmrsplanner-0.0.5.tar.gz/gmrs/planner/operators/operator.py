
import abc

from gmrs.evaluation.evaluation import Evaluation

from ..submodel import SubModel
from ..estimator import Estimator


class Operator:
    base: Estimator = None

    def __init__(self, base):
        self.base = base

    @abc.abstractclassmethod
    def eval(self, submodel: SubModel) -> [Evaluation]:
        pass

