import itertools
import random
from typing import List, Iterable


def flatten(lt: List[Iterable]) -> List:
    """
    Convert 2d list to 1d list

    :param lt: 2D array
    :return:
    """
    return list(itertools.chain.from_iterable(lt))


def shuffle(*ls):
    """
    Shuffle multi list

    :param ls: lists
    :return: shuffle list
    """
    lt = list(zip(*ls))
    random.shuffle(lt)
    return zip(*lt)
