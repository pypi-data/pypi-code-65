from savvihub.common.store import get_experiment
from savvihub.common.utils import get_token_from_config


def log(step, row=None):
    """
    step: a step for each iteration (required)
    row: a dictionary to log
    """
    experiment = get_experiment()
    experiment.log(step, row)
