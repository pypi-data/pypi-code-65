class Error:
    @classmethod
    def process(cls, status_code: int, message) -> dict:
        if status_code >= 500:
            return {
                'status_code': status_code
            }

        return {
            'status_code': status_code,
            'errors': message
        }
