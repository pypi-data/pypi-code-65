import enum


class State(enum.Enum):
    Idle = 1
    Running = 2
    Error = 3


class Message:
    def __init__(self, source, state, msg=None):
        self.source = source
        self.state = state
        self.msg = msg
