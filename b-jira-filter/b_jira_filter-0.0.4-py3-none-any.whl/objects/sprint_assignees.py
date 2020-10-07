from dataclasses import dataclass
from typing import List, Dict, Iterator

from b_jira_filter.objects.assignee import Assignee
from b_jira_filter.objects.sprint_issue import SprintIssue


@dataclass
class SprintAssignees:
    """
    Container class that holds sprint issues and works with issues assignees.
    """
    completed_sprint_issues: List[SprintIssue]
    not_completed_sprint_issues: List[SprintIssue]

    def aggregate(self) -> Dict[str, Assignee]:
        """
        Aggregates issues by assignees.

        :return: Aggregated issues.
        """
        agg = {}

        for issue in self.completed_sprint_issues + self.not_completed_sprint_issues:
            agg[issue.assignee] = Assignee()

        for issue in self.completed_sprint_issues:
            agg[issue.assignee].add_completed_issue(issue)

        for issue in self.not_completed_sprint_issues:
            agg[issue.assignee].add_not_completed_issue(issue)

        return agg

    def report(self) -> str:
        """
        Creates a human readable report.

        :return: Report string.
        """
        return '\n'.join(list(self.__individual_reports()))

    def __individual_reports(self) -> Iterator[str]:
        """
        Creates and individual report for every assignee.

        :return: Iterator instance over every individual report.
        """
        for key, value in self.aggregate().items():
            name = key.split('#')[1]
            yield f'{name:30s}: {str(value)}'
