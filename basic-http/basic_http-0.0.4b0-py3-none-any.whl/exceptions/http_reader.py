class HttpReaderError(Exception):
    def __init__(self, ex):
        super().__init__(ex)


class InvalidHttpResponse(HttpReaderError):
    def __init__(self, ex):
        super().__init__(ex)