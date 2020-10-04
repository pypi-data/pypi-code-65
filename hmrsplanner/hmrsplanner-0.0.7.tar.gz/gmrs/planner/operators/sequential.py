import math

from gmrs.planner.outcome import Result, Outcome, is_failure
from gmrs.planner.evaluation import Evaluation
from gmrs.planner.submodel import IEvaluable

from .operator import Operator
from .ievaluator import IEvaluator

SEQ_OP = 'SEQ'


class Sequential(Operator, IEvaluator):
    code = SEQ_OP

    def __init__(self, base):
        super().__init__(base)

    def next_node(self, node, outcome):
        # any task failure within a sequential compound lead to failure
        if is_failure(outcome):
            return Result.FAILURE

        index = self.nodes.find(node)
        if index < len(self.nodes):
            return self.node[index + 1]
        else:
            return Result.SUCCESS

    def merge_outcomes(self, outcomes1, outcomes2) -> Outcome:
        for o1 in outcomes1:
            if is_failure(o1):
                yield o1
            else:
                for o2 in outcomes2:
                    out = Outcome()
                    self.base.seq_agg(out, o1, o2)

                    out.res = (
                        Result.FAILURE
                        if is_failure(o2)
                        else Result.SUCCESS)

                    yield out

    def eval(self, submodels: IEvaluable) -> [Evaluation]:
        return self.seq_eval(submodels)

    def seq_eval(self, submodels: IEvaluable) -> [Evaluation]:
        '''
        Evaluate submodels and aggregate results
        '''

        if len(submodels) == 1:
            return self.base.eval_single(submodels[0])
        else:
            # divide
            end = len(submodels)
            mid = math.floor(end/2)
            eval_l = self.seq_eval(submodels[0:mid])
            eval_r = self.seq_eval(submodels[mid:end])
            # conquer
            agg = self.base.combineGen(self.aggregate_evaluations,
                                       eval_l, eval_r)
            # agg = self.aggregate_evaluations(eval_l, eval_r)
            return agg

    def aggregate_evaluations(self, evals1: [Evaluation], evals2: [Evaluation]):
        res_configs = self.base.merge_configs(evals1.config, evals2.config)
        res_outs = self.merge_outcomes(evals1.outcomes, evals2.outcomes)
        return Evaluation(config=res_configs, outcomes=res_outs)

