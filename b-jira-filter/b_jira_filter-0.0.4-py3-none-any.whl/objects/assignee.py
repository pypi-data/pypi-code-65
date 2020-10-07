from typing import List

from b_jira_filter.objects.sprint_issue import SprintIssue
from b_jira_filter.objects.sprint_story_points import SprintStoryPoints


class Assignee:
    """
    A class representing a developer in a sprint.
    """
    def __init__(self):
        """
        Constructor.
        """
        self.__completed_issues: List[SprintIssue] = []
        self.__not_completed_issues: List[SprintIssue] = []

    def __str__(self):
        """
        String representation.

        :return: String representation.
        """
        return str(self.sprint_story_points())

    def add_completed_issue(self, issue: SprintIssue) -> None:
        """
        Adds an issue to a completed issues list.

        :param issue: A completed issue.

        :return: No return.
        """
        self.__completed_issues.append(issue)
        assert len(set([issue.assignee for issue in self.__completed_issues])) < 2, 'Multiple assignees detected.'

    def add_not_completed_issue(self, issue: SprintIssue) -> None:
        """
        Adds an issue to a not completed issues list.

        :param issue: A not completed issue.

        :return: No return.
        """
        self.__not_completed_issues.append(issue)
        assert len(set([issue.assignee for issue in self.__completed_issues])) < 2, 'Multiple assignees detected.'

    def sprint_story_points(self) -> SprintStoryPoints:
        """
        Calculates story points according to given issues.

        :return: Sprint story points.
        """
        points = SprintStoryPoints()

        for ci in self.__completed_issues:
            points.add_completed(ci.story_points)

        for ci in self.__not_completed_issues:
            points.add_not_completed(ci.story_points)

        return points
