import abc

from .evaluation import Evaluation


class IEvaluable:

    @abc.abstractmethod
    def eval(self) -> [Evaluation]:
        '''
        return ConfigEvaluation
        '''
        pass


class ConstantEvaluationSubmodel(IEvaluable):
    def __init__(self, evaluation):
        self.evaluation = evaluation

    def eval(self):
        yield self.evaluation


class MultipleConstantEvaluationsSubmodel(IEvaluable):
    def __init__(self, *evaluations):
        self.evaluations = evaluations

    def eval(self):
        return self.evaluations


class RefinedSubmodel(IEvaluable):
    def __init__(self, op, refinements: [IEvaluable]):
        self.op = op
        self.refinements = refinements
