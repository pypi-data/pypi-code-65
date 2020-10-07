import json
from typing import Tuple, List

import requests

from b_jira_filter.objects.credentials import Credentials
from b_jira_filter.objects.sprint_issue import SprintIssue


class SprintReport:
    """
    Class that works with JIRA sprint reports.
    """
    def __init__(self, credentials: Credentials, board_id: str, sprint_id: str):
        self.credentials = credentials
        self.board_id = board_id
        self.sprint_id = sprint_id

        self.url = (
            f'{self.credentials.server}/rest/greenhopper/latest/rapid/charts'
            f'/sprintreport?rapidViewId={self.board_id}&sprintId={self.sprint_id}'
        )

    def load(self) -> Tuple[List[SprintIssue], List[SprintIssue]]:
        """
        Downloads sprint report.

        :return: Completed and not completed issues in a given sprint.
        """
        response = requests.get(
            url=self.url,
            auth=self.credentials.basic_auth
        )

        if response.status_code != 200:
            raise requests.HTTPError(response.content.decode())

        text = json.loads(response.content.decode())

        completed_issues = text['contents']['completedIssues']
        completed_issues = [SprintIssue.from_dict(ci) for ci in completed_issues]

        not_completed_issues = text['contents']['issuesNotCompletedInCurrentSprint']
        not_completed_issues = [SprintIssue.from_dict(nci) for nci in not_completed_issues]

        return completed_issues, not_completed_issues
