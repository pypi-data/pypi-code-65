from b_jira_filter.getters.boards import Boards
from b_jira_filter.getters.sprint_report import SprintReport
from b_jira_filter.getters.sprints import Sprints
from b_jira_filter.objects.credentials import Credentials
from b_jira_filter.objects.sprint_assignees import SprintAssignees


def main() -> None:
    """
    Command that creates a story points report for a specific sprint.

    :return: No return.
    """
    credentials = Credentials()

    board = Boards(credentials.jira_sdk).prompt_select_board()
    sprint = Sprints(credentials.jira_sdk, board).prompt_select_sprint()

    completed, not_completed = SprintReport(credentials, board.id, sprint.id).load()
    sprint_assignees = SprintAssignees(completed, not_completed)

    print('\n\n----------------------------------------------------------------\n\n')
    print(sprint_assignees.report())
    print('\n\n----------------------------------------------------------------\n\n')
