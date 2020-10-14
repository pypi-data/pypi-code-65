class WrongStatusCodeException(Exception):
    def __str__(self):
        return "Twitter didn't return 2xx status"
