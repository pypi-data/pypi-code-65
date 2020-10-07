class ApiClientError(Exception):
    def __init__(self, code, body, message: str = None):
        msg = f"Response {code}: {body}; {message}"
        super(ApiClientError, self).__init__(msg)