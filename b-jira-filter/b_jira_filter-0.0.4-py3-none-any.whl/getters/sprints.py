from typing import List

from jira import JIRA
from jira.resources import Sprint, Board


class Sprints:
    """
    Class that works with JIRA sprints.
    """
    def __init__(self, jira: JIRA, board: Board):
        """
        Constructor.

        :param jira: JIRA SDK instance.
        :param board: A JIRA board in which sprints should be queried.
        """
        self.__jira = jira
        self.__board = board

    def get_sprints(self) -> List[Sprint]:
        """
        Lists all available sprints.

        :return: List of sprints.
        """
        return list(self.__jira.sprints(self.__board.id))

    def format(self, sprints: List[Sprint]) -> str:
        """
        Formats list of sprints into a human readable text.

        :param boards: List of sprints.

        :return: Human readable list.
        """
        return '\n'.join([f'{index + 1}. {str(sprint)}' for index, sprint in enumerate(sprints)])

    def prompt_select_sprint(self) -> Sprint:
        """
        Asks user for an input - asks to select a sprint from available sprints.

        :return: Selected sprint.
        """
        s = self.get_sprints()
        s_str = self.format(s)

        selected_sprint = None
        successful_select = False

        while not successful_select:
            try:
                user_input = input(f'\nSelect a sprint (1-{len(s)}):\n\n{s_str}\n\nSprint number[Default {len(s)}]: ')
                user_input = user_input if user_input != '' else len(s)
                selected_sprint = s[int(user_input) - 1]
            except (ValueError, KeyError, IndexError):
                print('\n-------------------------')
                print('Invalid number specified.')
                print('-------------------------\n')
            else:
                successful_select = True

        return selected_sprint
