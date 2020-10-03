class RequestError(Exception):
    def __init__(self, ex: str = ''):
        super().__init__(ex)


class RequestSendError(RequestError):
    def __init__(self, ex: str = ''):
        super().__init__(ex)
