class MultiKeyDictionaryError(KeyError):
    def __init__(self, ex):
        super().__init__(ex)


class KeyNotFound(MultiKeyDictionaryError):
    def __init__(self, ex):
        super().__init__(ex)


class WrongKeyType(Exception):
    def __init__(self, ex):
        super().__init__(ex)


class WrongHttpHeaderDataType(Exception):
    def __init__(self, ex):
        super().__init__(ex)
