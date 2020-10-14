class PumpError(Exception):
    """
    General pump error
    """

    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return self.msg


class PumpOverloadError(PumpError):
    """
    Error that the pump is in a state of overload or an incorrect command string was sent
    """

    def __init__(self):
        super().__init__(msg='Error that the pump is in a state of overload or an incorrect command string was sent')


class CommandError(Exception):
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return self.msg
