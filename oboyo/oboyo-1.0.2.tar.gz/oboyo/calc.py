"""Calculations module."""

'''
import calc
temp = calc.Calc(2, 3)
temp.add()
'''
# Let calc be module instead

from typing import Union


class Calc:

    # Constructor
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    @staticmethod
    def add(x, y):
        # Type hints comments that are backwards compatiable with Python 2.
        # type: (Union[int, float], Union[int, float]) -> Union[int, float]
        return x + y

    @staticmethod
    def multiply(x, y):
        # Type hints comments that are backwards compatiable with Python 2.
        # type: (Union[int, float], Union[int, float]) -> Union[int, float]
        return x * y


class Distance(Calc):

    def __init__(self, x):
        super().__init__(x, x)

    @staticmethod
    def power(x):
        # Type hints comments that are backwards compatiable with Python 2.
        # type: (Union[int, float]) -> Union[int, float]
        return x ** 2
