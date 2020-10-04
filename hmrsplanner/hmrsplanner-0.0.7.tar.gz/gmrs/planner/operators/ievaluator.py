import abc

from gmrs.planner.evaluation import Evaluation
from ..submodel import IEvaluable


class IEvaluator:
    """
    docstring
    """

    @abc.abstractclassmethod
    def eval(self, submodels: [IEvaluable]) -> [Evaluation]:
        pass
