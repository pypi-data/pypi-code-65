from typing import List

from jira import JIRA
from jira.resources import Board


class Boards:
    """
    Class that works with JIRA boards.
    """
    def __init__(self, jira: JIRA):
        """
        Constructor.

        :param jira: JIRA SDK instance.
        """
        self.__jira = jira

    def get_boards(self) -> List[Board]:
        """
        Gets all available boards in JIRA.

        :return: List of boards.
        """
        return list(self.__jira.boards())

    def format(self, boards: List[Board]) -> str:
        """
        Formats list of boards into a human readable text.

        :param boards: List of boards.

        :return: Human readable list.
        """
        return '\n'.join([f'{index + 1}. {board}' for index, board in enumerate(boards)])

    def prompt_select_board(self) -> Board:
        """
        Asks user for an input - asks to select a board from available boards.

        :return: Selected board.
        """
        b = self.get_boards()
        b_str = self.format(b)

        selected_board = None
        successful_select = False

        while not successful_select:
            try:
                user_input = input(f'\nSelect a board (1-{len(b)}):\n\n{b_str}\n\nBoard number[Default 1]: ')
                user_input = user_input if user_input != '' else 1
                selected_board = b[int(user_input) - 1]
            except (ValueError, KeyError, IndexError):
                print('\n-------------------------')
                print('Invalid number specified.')
                print('-------------------------\n')
            else:
                successful_select = True

        return selected_board
