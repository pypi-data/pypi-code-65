import os

import requests

from savvihub.common.config import config
from savvihub.common.experiment import Experiment
from savvihub.common.savvihub import SavviHubClient


experiment = None
token = None


def get_token():
    global token
    if not token:
        token = os.getenv('EXPERIMENT_ACCESS_TOKEN')
    return token


def get_experiment():
    global experiment

    if not experiment:
        token = get_token()
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
        experiment = Experiment.from_given_or_global_config(config, client)

    return experiment
