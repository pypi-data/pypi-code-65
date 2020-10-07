from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class SprintIssue:
    """
    A sprint issue representation class.
    """
    id: str
    key: str
    done: str
    assigned_account_id: str
    assignee_name: str
    story_points: int

    @property
    def assignee(self) -> str:
        """
        Assignee field.

        :return: Asignee representation field string.
        """
        return f'{self.assigned_account_id}#{self.assignee_name}'

    @staticmethod
    def from_dict(serialized_issue: Dict[str, Any]) -> 'SprintIssue':
        """
        Creates an instance from a dictionary.

        :param serialized_issue: Dictionary representation of a sprint issue.

        :return: Sprint issue instance.
        """
        estimate = serialized_issue.get('estimateStatistic', serialized_issue.get('currentEstimateStatistic', {}))
        story_points = int(estimate.get('statFieldValue', {}).get('value', 0))

        return SprintIssue(
            serialized_issue['id'],
            serialized_issue['key'],
            serialized_issue['done'],
            serialized_issue['assigneeAccountId'],
            serialized_issue['assigneeName'],
            story_points
        )
