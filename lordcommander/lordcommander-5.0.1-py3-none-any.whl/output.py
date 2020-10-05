"""
---------------------------------------------------------------------
output.py
---------------------------------------------------------------------
This module provides a fancy way to show output, errors, warnings,
or info on CLI.

Version: 5.x
License: GNU General Public License 3
"""

from colr import color


class Output:
    """Handles all output messages and formats them according to specified color code."""

    # Message color codes
    SUCCESS = 'GREEN'
    INFO = '0060a0'
    WARNING = 'YELLOW'
    DANGER = 'RED'
    MUTED = '6a6a6a'

    @staticmethod
    def write(message, code='', end='\n'):
        """
        Shows message according to color code in terminal. If message has several parts,
        you can pass a list of dictionaries as {text: 'Message', code: 'ffffff'} format.
        :param message: str | list
        :param code: str
        :param end: str
        :return: None
        """
        if isinstance(message, list):
            for segment in message:
                Output.write(
                    color(f"{segment['text']}", fore=segment['code']), end=' ')
            print('\n')
            return

        print(color(f"{message}", fore=code), end=end)

    @staticmethod
    def normal(message, end='\n'):
        Output.write(message, end=end)

    @staticmethod
    def success(message, end='\n'):
        Output.write(message, code=Output.SUCCESS, end=end)

    @staticmethod
    def info(message, end='\n'):
        Output.write(message, code=Output.INFO, end=end)

    @staticmethod
    def warning(message, end='\n'):
        Output.write(message, code=Output.WARNING, end=end)

    @staticmethod
    def danger(message, end='\n'):
        Output.write(message, code=Output.DANGER, end=end)

    @staticmethod
    def muted(message, end='\n'):
        Output.write(message, code=Output.MUTED, end=end)
