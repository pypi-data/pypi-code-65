from enum import Enum


class Result(Enum):
    FAILURE = 0
    SUCCESS = 1


class Outcome:
    # type = None
    def __init__(self, p=None, res: Result = None, **rewards):
        self.p = p
        self.res = res
        for key, value in rewards.items():
            setattr(self, key, value)

    def get(self, name: str):
        return getattr(self, name)

    def set(self, name: str, value: any):
        setattr(self, name, value)


def is_success(outcome: Outcome):
    return outcome.res == Result.SUCCESS


def is_failure(outcome: Outcome):
    return outcome.res == Result.FAILURE
