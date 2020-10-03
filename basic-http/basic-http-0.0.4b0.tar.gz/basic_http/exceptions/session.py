class SessionError(Exception):
    def __init__(self, ex: str = ''):
        super().__init__(ex)


class HostUnreachable(SessionError):
    def __init__(self, ex: str = ''):
        super().__init__(ex)
