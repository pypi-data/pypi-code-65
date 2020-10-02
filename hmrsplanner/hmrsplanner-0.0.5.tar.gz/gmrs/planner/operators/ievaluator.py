import abc

from gmrs.evaluation.evaluation import Evaluation
from ..submodel import SubModel


class IEvaluator:
    """
    docstring
    """

    @abc.abstractclassmethod
    def eval(self, submodels: [SubModel]) -> [Evaluation]:
        pass
