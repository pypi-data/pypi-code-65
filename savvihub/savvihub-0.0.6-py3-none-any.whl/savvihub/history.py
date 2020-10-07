from datetime import datetime

from savvihub.savvihub_cli.constants import DEFAULT_CONFIG_PATH
from savvihub.savvihub_cli.utils import get_token_from_config
from savvihub.savvihub_cli.savvihub import SavviHubClient


class History:
    def __init__(self, experiment):
        self.experiment = experiment
        self.rows = []
        self._step_index = 0

    def update(self, step, row):
        """
        Update row in history
        """
        for k, v in row.items():
            if type(v) != str:
                row[k] = str(v)

        row["step"] = str(step)
        row["created_dt"] = datetime.utcnow().isoformat()
        self.request(row)
        self.rows.append(row)

    def request(self, row):
        token = get_token_from_config(DEFAULT_CONFIG_PATH)
        client = SavviHubClient(token=token)
        _ = client.experiment_progress_update(self.experiment.experiment_id, row)
