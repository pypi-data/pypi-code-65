class BadCookie(Exception):
    def __init__(self, ex: str = ''):
        super().__init__(ex)


class CookieManagerNoDomainProvided(BadCookie):
    def __init__(self, ex: str = ''):
        super().__init__(ex)
