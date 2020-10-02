from gmrs.evaluation.outcome import Outcome
from gmrs.services.base import BaseService


class ObjectiveSystem:
    @staticmethod
    def seq_agg(res: Outcome, outcome1: Outcome, outcome2: Outcome):
        pass


class BaseObjectiveSystem(ObjectiveSystem, BaseService):
    pass
