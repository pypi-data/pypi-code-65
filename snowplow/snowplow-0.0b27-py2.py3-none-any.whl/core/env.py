import os


class Env:
    @classmethod
    def AWS_DEFAULT_REGION(cls, default=None):
        return os.environ.get('AWS_DEFAULT_REGION', default)

    @classmethod
    def AWS_ACCESS_KEY_ID(cls, default=None):
        return os.environ.get('AWS_ACCESS_KEY_ID', default)

    @classmethod
    def AWS_SECRET_ACCESS_KEY(cls, default=None):
        return os.environ.get('AWS_SECRET_ACCESS_KEY', default)
