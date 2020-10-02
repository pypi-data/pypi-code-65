import abc


class SubModel:

    @abc.abstractmethod
    def eval(self):
        '''
        return ConfigEvaluation
        '''
        pass


class ConstantEvaluationSubmodel(SubModel):
    def __init__(self, evaluation):
        self.evaluation = evaluation


class MultipleConstantEvaluationsSubmodel(SubModel):
    def __init__(self, *evaluations):
        self.evaluations = evaluations

    def eval(self):
        return self.evaluations


class RefinedSubmodel(SubModel):
    def __init__(self, op, refinements: [SubModel]):
        self.op = op
        self.refinements = refinements
