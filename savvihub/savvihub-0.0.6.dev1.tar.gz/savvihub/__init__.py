import os

import requests

from savvihub.savvihub_cli.config import config
from savvihub.savvihub_cli.constants import DEFAULT_CONFIG_PATH
from savvihub.savvihub_cli.savvihub import SavviHubClient

from savvihub.experiment import Experiment
from savvihub.savvihub_cli.utils import get_token_from_config

experiment = None


def get_experiment():
    global experiment

    if not experiment:
        token = os.getenv('EXPERIMENT_ACCESS_TOKEN')
        if not token:
            print("EXPERIMENT_ACCESS_TOKEN is not provided as an environment variable")

        client = SavviHubClient(token=token)

        try:
            savvihub_experiment = client.experiment_read(raise_error=True).json()
        except requests.exceptions.HTTPError as e:
            print(f"Http Error: {e}")
            return
        except requests.exceptions.ConnectionError as e:
            print(f"Connection Error:{e}")
            return
        except requests.exceptions.Timeout as e:
            print(f"Timeout Error: {e}")
            return
        except requests.exceptions.TooManyRedirects as e:
            print(f"Too many Redirects Error: {e}")
            return
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        config.experiment_id = savvihub_experiment.get("id")
        experiment = Experiment.from_given_or_global_config(config)

    return experiment


def log(step, row=None):
    """
    step: a step for each iteration (required)
    row: a dictionary to log
    """
    experiment = get_experiment()
    experiment.log(step, row)
