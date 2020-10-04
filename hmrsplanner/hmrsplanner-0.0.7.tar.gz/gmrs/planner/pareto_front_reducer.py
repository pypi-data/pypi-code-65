import numpy as np

from .evaluation import Evaluation
from ..objective.property_base import Property, PropertyType

from ..objective.utils import avg_properties
from .outcome import Outcome


class ParetoFrontReducer:
    """ 
        Evaluates to the Pareto Frontier of submodels
        
        Enumerate all the evaluations of wrapped model
        at the evaluation and find the Pareto Frontier.

        Only success outcomes are considered?
    """

    def __init__(self, objective):
        self.objective = objective

    def pipe(self, origin: [Evaluation]) -> [Evaluation]:
        costs = []
        evaluations = []
        for evaluation in origin:
            e_costs = avg_properties(evaluation,
                                     self.objective.properties)
            costs.append(to_costs_arr(e_costs, self.objective.properties))
            evaluations.append(evaluation)

        is_efficient_map = is_pareto_efficient(np.array(costs))
        frontier = []
        for i, is_efficient in enumerate(is_efficient_map):
            if is_efficient:
                frontier.append(evaluations[i])
        return frontier


def to_costs_arr(outcome: Outcome, properties: [Property]):
    arr = []
    for os in properties:
        value = os.to_cost(outcome)
        arr.append(value)
    return arr


def is_pareto_efficient(costs):
    """
    Find the pareto-efficient points
    :param costs: An (n_points, n_costs) array
    :return: A (n_points, ) boolean array, indicating
        whether each point is Pareto efficient
    """
    is_efficient = np.ones(costs.shape[0], dtype=bool)
    for i, c in enumerate(costs):
        if is_efficient[i]:
            is_efficient[is_efficient] = np.any(
                costs[is_efficient] < c, axis=1)
            # Keep any point with a lower cost

            is_efficient[i] = True  # And keep self
    return is_efficient
