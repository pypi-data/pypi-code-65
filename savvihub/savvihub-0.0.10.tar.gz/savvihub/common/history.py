from datetime import datetime

from savvihub.common.store import get_token
from savvihub.common.savvihub import SavviHubClient


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
        token = get_token()
        client = SavviHubClient(token=token)
        _ = client.experiment_progress_update(self.experiment.experiment_id, row)
