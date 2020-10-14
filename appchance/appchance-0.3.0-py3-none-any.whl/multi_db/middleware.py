from appchance.multi_db import db_config


class MultiDatabaseMiddlewareAbstract:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        db_config.db = self._get_db_name(request=request)

        response = self.get_response(request)

        if hasattr(db_config, "db"):
            del db_config.db

        return response

    class Meta:
        abstract = True

    def _get_db_name(self, request):
        raise NotImplementedError
