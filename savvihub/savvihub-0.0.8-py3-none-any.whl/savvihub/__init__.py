from savvihub.common.store import get_experiment
from savvihub.savvihub_cli.config import config
from savvihub.savvihub_cli.constants import DEFAULT_CONFIG_PATH
from savvihub.savvihub_cli.savvihub import SavviHubClient

from savvihub.experiment import Experiment
from savvihub.savvihub_cli.utils import get_token_from_config

experiment = None


def log(step, row=None):
    """
    step: a step for each iteration (required)
    row: a dictionary to log
    """
    experiment = get_experiment()
    experiment.log(step, row)
